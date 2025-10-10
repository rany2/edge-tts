#!/usr/bin/env python3
"""
Batch Processing & Queue Management for Edge-TTS

This example demonstrates advanced batch processing capabilities including:
- Priority-based task queues
- Concurrent processing with rate limiting
- Progress tracking and monitoring
- Error handling and retry mechanisms
- Resource management and optimization
- Database integration for large-scale processing
"""

import asyncio
import json
import logging
import time
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import edge_tts
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import os

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

class TaskStatus(Enum):
    """Task status states"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"

@dataclass
class TTSBatchTask:
    """Individual TTS task in batch"""
    task_id: str
    text: str
    voice: str
    output_file: str
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class BatchConfig:
    """Configuration for batch processing"""
    max_concurrent_tasks: int = 5
    rate_limit_per_minute: int = 100
    retry_delay_seconds: int = 30
    max_retry_attempts: int = 3
    database_path: str = "tts_batch.db"
    output_directory: str = "batch_output"
    enable_progress_tracking: bool = True
    enable_notifications: bool = True

class TTSBatchProcessor:
    """Advanced batch processor for TTS tasks"""
    
    def __init__(self, config: BatchConfig):
        self.config = config
        self.task_queue = asyncio.PriorityQueue()
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Dict[str, TTSBatchTask] = {}
        self.failed_tasks: Dict[str, TTSBatchTask] = {}
        self.rate_limiter = asyncio.Semaphore(config.max_concurrent_tasks)
        self.is_running = False
        self.progress_callbacks: List[Callable] = []
        
        # Initialize database
        self._init_database()
        
        # Create output directory
        os.makedirs(config.output_directory, exist_ok=True)
    
    def _init_database(self):
        """Initialize SQLite database for task tracking"""
        conn = sqlite3.connect(self.config.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tts_tasks (
                task_id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                voice TEXT NOT NULL,
                output_file TEXT NOT NULL,
                priority INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                error_message TEXT,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def add_task(self, task: TTSBatchTask):
        """Add a task to the processing queue"""
        # Save to database
        self._save_task_to_db(task)
        
        # Add to priority queue (higher priority = lower number)
        priority_value = 6 - task.priority.value  # Invert for priority queue
        await self.task_queue.put((priority_value, task.created_at, task))
        
        logging.info(f"Added task {task.task_id} with priority {task.priority.name}")
    
    async def add_batch_tasks(self, tasks: List[TTSBatchTask]):
        """Add multiple tasks to the processing queue"""
        for task in tasks:
            await self.add_task(task)
        
        logging.info(f"Added {len(tasks)} tasks to batch queue")
    
    async def start_processing(self):
        """Start the batch processing"""
        if self.is_running:
            raise RuntimeError("Batch processor is already running")
        
        self.is_running = True
        logging.info("Starting batch processing...")
        
        # Start processing loop
        processing_task = asyncio.create_task(self._processing_loop())
        
        # Start monitoring task
        monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        try:
            await asyncio.gather(processing_task, monitoring_task)
        except asyncio.CancelledError:
            logging.info("Batch processing cancelled")
        finally:
            self.is_running = False
    
    async def stop_processing(self):
        """Stop the batch processing"""
        self.is_running = False
        logging.info("Stopping batch processing...")
    
    async def _processing_loop(self):
        """Main processing loop"""
        while self.is_running:
            try:
                # Get next task from queue
                priority, created_at, task = await asyncio.wait_for(
                    self.task_queue.get(), timeout=1.0
                )
                
                # Check rate limiting
                await self._rate_limit_check()
                
                # Process task
                await self._process_single_task(task)
                
            except asyncio.TimeoutError:
                # No tasks available, continue
                continue
            except Exception as e:
                logging.error(f"Error in processing loop: {e}")
                await asyncio.sleep(1)
    
    async def _process_single_task(self, task: TTSBatchTask):
        """Process a single TTS task"""
        async with self.rate_limiter:
            try:
                # Update task status
                task.status = TaskStatus.PROCESSING
                task.started_at = datetime.now()
                self._update_task_in_db(task)
                
                # Create TTS communicate instance
                communicate = edge_tts.Communicate(
                    task.text,
                    task.voice
                )
                
                # Generate audio
                output_path = os.path.join(self.config.output_directory, task.output_file)
                await communicate.save(output_path)
                
                # Mark as completed
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                self.completed_tasks[task.task_id] = task
                self._update_task_in_db(task)
                
                logging.info(f"Completed task {task.task_id}")
                await self._notify_progress(task)
                
            except Exception as e:
                # Handle task failure
                await self._handle_task_failure(task, str(e))
    
    async def _handle_task_failure(self, task: TTSBatchTask, error_message: str):
        """Handle task failure with retry logic"""
        task.retry_count += 1
        task.error_message = error_message
        
        if task.retry_count < task.max_retries:
            # Retry task
            task.status = TaskStatus.RETRYING
            self._update_task_in_db(task)
            
            # Wait before retry
            await asyncio.sleep(self.config.retry_delay_seconds)
            
            # Re-queue task
            priority_value = 6 - task.priority.value
            await self.task_queue.put((priority_value, task.created_at, task))
            
            logging.warning(f"Retrying task {task.task_id} (attempt {task.retry_count})")
        else:
            # Mark as failed
            task.status = TaskStatus.FAILED
            self.failed_tasks[task.task_id] = task
            self._update_task_in_db(task)
            
            logging.error(f"Task {task.task_id} failed after {task.retry_count} attempts")
            await self._notify_progress(task)
    
    async def _rate_limit_check(self):
        """Check and enforce rate limiting"""
        # Simple rate limiting implementation
        # In production, you'd want more sophisticated rate limiting
        await asyncio.sleep(0.1)  # Small delay to prevent overwhelming the service
    
    async def _monitoring_loop(self):
        """Monitor processing status and health"""
        while self.is_running:
            try:
                # Log current status
                queue_size = self.task_queue.qsize()
                active_count = len(self.active_tasks)
                completed_count = len(self.completed_tasks)
                failed_count = len(self.failed_tasks)
                
                logging.info(
                    f"Queue: {queue_size}, Active: {active_count}, "
                    f"Completed: {completed_count}, Failed: {failed_count}"
                )
                
                # Check for stuck tasks
                await self._check_stuck_tasks()
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _check_stuck_tasks(self):
        """Check for tasks that have been processing too long"""
        current_time = datetime.now()
        stuck_threshold = timedelta(minutes=10)  # 10 minutes timeout
        
        for task_id, task in list(self.active_tasks.items()):
            if task.started_at and (current_time - task.started_at) > stuck_threshold:
                logging.warning(f"Task {task_id} appears to be stuck, cancelling...")
                task.cancel()
                del self.active_tasks[task_id]
    
    async def _notify_progress(self, task: TTSBatchTask):
        """Notify progress callbacks"""
        for callback in self.progress_callbacks:
            try:
                await callback(task)
            except Exception as e:
                logging.error(f"Error in progress callback: {e}")
    
    def add_progress_callback(self, callback: Callable):
        """Add a progress callback function"""
        self.progress_callbacks.append(callback)
    
    def _save_task_to_db(self, task: TTSBatchTask):
        """Save task to database"""
        conn = sqlite3.connect(self.config.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO tts_tasks 
            (task_id, text, voice, output_file, priority, status, created_at, 
             started_at, completed_at, retry_count, max_retries, error_message, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.task_id, task.text, task.voice, task.output_file,
            task.priority.value, task.status.value, task.created_at,
            task.started_at, task.completed_at, task.retry_count,
            task.max_retries, task.error_message, json.dumps(task.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def _update_task_in_db(self, task: TTSBatchTask):
        """Update task in database"""
        conn = sqlite3.connect(self.config.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tts_tasks SET 
            status = ?, started_at = ?, completed_at = ?, 
            retry_count = ?, error_message = ?, metadata = ?
            WHERE task_id = ?
        ''', (
            task.status.value, task.started_at, task.completed_at,
            task.retry_count, task.error_message, json.dumps(task.metadata),
            task.task_id
        ))
        
        conn.commit()
        conn.close()
    
    def get_task_status(self, task_id: str) -> Optional[TTSBatchTask]:
        """Get task status by ID"""
        return (
            self.completed_tasks.get(task_id) or
            self.failed_tasks.get(task_id) or
            self.active_tasks.get(task_id)
        )
    
    def get_batch_statistics(self) -> Dict[str, Any]:
        """Get batch processing statistics"""
        return {
            "queue_size": self.task_queue.qsize(),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "is_running": self.is_running,
            "config": asdict(self.config)
        }

class BatchTaskManager:
    """High-level manager for batch TTS operations"""
    
    def __init__(self, config: BatchConfig = None):
        self.config = config or BatchConfig()
        self.processor = TTSBatchProcessor(self.config)
        self.task_counter = 0
    
    def create_task(self, text: str, voice: str, output_file: str, 
                   priority: TaskPriority = TaskPriority.NORMAL,
                   metadata: Dict[str, Any] = None) -> TTSBatchTask:
        """Create a new TTS task"""
        self.task_counter += 1
        task_id = f"task_{self.task_counter}_{int(time.time())}"
        
        return TTSBatchTask(
            task_id=task_id,
            text=text,
            voice=voice,
            output_file=output_file,
            priority=priority,
            metadata=metadata or {}
        )
    
    async def process_text_batch(self, texts: List[str], voice: str, 
                                output_prefix: str = "batch") -> List[str]:
        """Process a batch of texts"""
        tasks = []
        output_files = []
        
        for i, text in enumerate(texts):
            output_file = f"{output_prefix}_{i:04d}.mp3"
            task = self.create_task(text, voice, output_file)
            tasks.append(task)
            output_files.append(output_file)
        
        # Add tasks to processor
        await self.processor.add_batch_tasks(tasks)
        
        return output_files
    
    async def process_priority_batch(self, high_priority_texts: List[str],
                                   normal_priority_texts: List[str],
                                   voice: str) -> Dict[str, List[str]]:
        """Process texts with different priorities"""
        # Create high priority tasks
        high_priority_tasks = []
        for i, text in enumerate(high_priority_texts):
            task = self.create_task(
                text, voice, f"urgent_{i:04d}.mp3", 
                priority=TaskPriority.HIGH
            )
            high_priority_tasks.append(task)
        
        # Create normal priority tasks
        normal_priority_tasks = []
        for i, text in enumerate(normal_priority_texts):
            task = self.create_task(
                text, voice, f"normal_{i:04d}.mp3",
                priority=TaskPriority.NORMAL
            )
            normal_priority_tasks.append(task)
        
        # Add all tasks
        await self.processor.add_batch_tasks(high_priority_tasks + normal_priority_tasks)
        
        return {
            "high_priority": [task.output_file for task in high_priority_tasks],
            "normal_priority": [task.output_file for task in normal_priority_tasks]
        }

# Example usage and demonstrations
async def example_basic_batch_processing():
    """Example: Basic batch processing"""
    print("=== Basic Batch Processing Example ===")
    
    config = BatchConfig(
        max_concurrent_tasks=3,
        rate_limit_per_minute=50,
        output_directory="basic_batch_output"
    )
    
    manager = BatchTaskManager(config)
    
    # Create sample texts
    texts = [
        "Welcome to our podcast episode one.",
        "Today we'll be discussing artificial intelligence.",
        "Machine learning is revolutionizing technology.",
        "Natural language processing is fascinating.",
        "Thank you for listening to our show."
    ]
    
    # Process batch
    output_files = await manager.process_text_batch(
        texts, "en-US-AriaNeural", "podcast_episode"
    )
    
    print(f"Created {len(output_files)} audio files")
    for file in output_files:
        print(f"- {file}")

async def example_priority_batch_processing():
    """Example: Priority-based batch processing"""
    print("\n=== Priority Batch Processing Example ===")
    
    config = BatchConfig(
        max_concurrent_tasks=2,
        rate_limit_per_minute=30
    )
    
    manager = BatchTaskManager(config)
    
    # High priority texts (urgent announcements)
    urgent_texts = [
        "URGENT: System maintenance in 5 minutes.",
        "CRITICAL: Database backup required immediately."
    ]
    
    # Normal priority texts (regular content)
    normal_texts = [
        "Welcome to our regular programming.",
        "Today's weather forecast.",
        "Sports updates for today."
    ]
    
    # Process with different priorities
    results = await manager.process_priority_batch(
        urgent_texts, normal_texts, "en-US-GuyNeural"
    )
    
    print("High priority files:")
    for file in results["high_priority"]:
        print(f"- {file}")
    
    print("Normal priority files:")
    for file in results["normal_priority"]:
        print(f"- {file}")

async def example_large_scale_processing():
    """Example: Large-scale processing with monitoring"""
    print("\n=== Large-Scale Processing Example ===")
    
    config = BatchConfig(
        max_concurrent_tasks=5,
        rate_limit_per_minute=100,
        output_directory="large_scale_output"
    )
    
    processor = TTSBatchProcessor(config)
    
    # Add progress callback
    async def progress_callback(task: TTSBatchTask):
        print(f"Progress: {task.task_id} - {task.status.value}")
    
    processor.add_progress_callback(progress_callback)
    
    # Create many tasks
    tasks = []
    for i in range(20):
        task = TTSBatchTask(
            task_id=f"large_scale_{i}",
            text=f"This is task number {i} in our large-scale processing batch.",
            voice="en-US-JennyNeural",
            output_file=f"large_scale_{i:04d}.mp3",
            priority=TaskPriority.NORMAL
        )
        tasks.append(task)
    
    # Add tasks to processor
    await processor.add_batch_tasks(tasks)
    
    # Start processing
    processing_task = asyncio.create_task(processor.start_processing())
    
    # Monitor for a while
    await asyncio.sleep(10)
    
    # Stop processing
    await processor.stop_processing()
    processing_task.cancel()
    
    # Get statistics
    stats = processor.get_batch_statistics()
    print(f"\nFinal Statistics: {stats}")

async def example_error_handling_and_retry():
    """Example: Error handling and retry mechanisms"""
    print("\n=== Error Handling Example ===")
    
    config = BatchConfig(
        max_concurrent_tasks=2,
        retry_delay_seconds=5,
        max_retry_attempts=2
    )
    
    processor = TTSBatchProcessor(config)
    
    # Create tasks with some that might fail
    tasks = [
        TTSBatchTask(
            task_id="good_task_1",
            text="This is a normal task that should work fine.",
            voice="en-US-AriaNeural",
            output_file="good_1.mp3"
        ),
        TTSBatchTask(
            task_id="good_task_2",
            text="Another normal task for processing.",
            voice="en-US-GuyNeural",
            output_file="good_2.mp3"
        ),
        # This task might fail due to very long text
        TTSBatchTask(
            task_id="problematic_task",
            text="This is an extremely long text that might cause issues " * 100,
            voice="en-US-JennyNeural",
            output_file="problematic.mp3",
            max_retries=2
        )
    ]
    
    await processor.add_batch_tasks(tasks)
    
    # Start processing
    processing_task = asyncio.create_task(processor.start_processing())
    
    # Let it run for a while
    await asyncio.sleep(15)
    
    # Stop and check results
    await processor.stop_processing()
    processing_task.cancel()
    
    # Check final status
    for task in tasks:
        status = processor.get_task_status(task.task_id)
        if status:
            print(f"Task {task.task_id}: {status.status.value}")
            if status.error_message:
                print(f"  Error: {status.error_message}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Batch Processing & Queue Management Examples")
    print("=" * 50)
    
    # Run examples
    asyncio.run(example_basic_batch_processing())
    asyncio.run(example_priority_batch_processing())
    asyncio.run(example_large_scale_processing())
    asyncio.run(example_error_handling_and_retry())
    
    print("\nAll batch processing examples completed!")

import asyncio
import edge_tts
from edge_tts.communicate import Communicate

TEXT = "你穿越大明成为第一贪官,入股赌坊兴办青楼,是沛县最大的保护伞,你更是当众受贿,万两白银,打点官职,就连沈安的县衙前院你都毫无避讳地摆满了金尊琉璃,可百姓非但不骂你,还纷纷求你多贪点,你本想就这样做个贪官逍遥一生,没想到朱元璋为追封祖地,乔装来到了你的属地,他一下就被你属地的沥青马路给震惊,黑面的马路不仅笔直平整,还有特殊规定,马车走在中间,行人只能走两边,这让朱元璋他们的马车畅通无阻,他又发现这周围两边行走的百姓一个个脸上洋溢着笑容,仿佛不为生活而发愁,朱元璋微微触动,这样的一幕,若是发生在盛唐,富宋倒也没什么,可如今是明朝初期,长期无休止的战争,消耗了大量人力财力,更有战争爆发频繁的地区,土地荒废,十里不见人烟。朱元璋想到之前的一幕幕,心中觉得太不可思议。马车继续往前行驶,来到了县门口,一位捕快伸出一只手,示意他们停车。这整个商队都是你的？闻言,朱元璋微微一愣,立即懂得对方的个话里的意思,不就是看他们都是外地商人,想要趁机捞上一笔。朱元璋的脸色一沉,但也没有多说什么,一个眼神过去,旁边的侍卫就掏出了一盒银子,捕快却一脸义正言辞地说,这是干什么的？他就是关心的问候一下吗？塞给自己钱干嘛？你们不收这个吗？朱元璋脸色好看了一些,但还是有些疑惑,捕快说到：我是看你们身家富有,所以想给你们提点建议,看到没进县门之后,沿着东边直走那条街上都是高档客栈,专门给你们这种有钱人住。朱元璋有些愣住,见他似乎有兴趣,捕快接着给他说了起来。是啊,来咱们沛县,你还不得先知道这里的场所划分吗。东边管住宿,南边管吃喝玩乐,西边是购物集市,找官府的话就去北面,想投资做生意,就去那边找咱们的县太爷,有点意思。朱元璋捋了捋胡,城卫捕快给介绍当地环境的,以前哪次不是塞银子,一行人穿过县门进入沛县,可没走几步路,便不由瞪大大眼睛,充满烟火气息的大街上,每一个人脸上都洋溢着其他地方看不到的笑容。朱元璋一行人走在大街上,有种恍若隔世的感觉,街上上开着各种的铺子,这里的行各业都有连青楼赌坊的旗子,也高高挂起.“一个小县,竟然如此繁华！”朱元璋微微沉思无比触动,马皇后露出亲和的笑容,微微点点头,很快,他们就来到了东区,朱元璋又是大开眼界,入眼望去,这里的房子竟然跟他们见到的寻常房子完全不同,这些房子竟然修得一栋一栋的,一排排过去,矗立了一大片,而且每一栋都修了四五层。朱彪和朱爽二人脸色也极为惊讶,虽然比不上金砖银瓦的皇宫,风格却见所未见。当朱元璋入住后,走到阳台上,看见沛县的全貌,几个区域也尽在他的眼下,他不禁感慨道“沛县治理的如此之好,这孟胤必是能臣。”"
VOICE = "zh-CN-YunxiNeural"
OUTPUT_FILE = "test.mp3"
WEBVTT_FILE = "test.vtt"

async def amain() -> None:
    """Main function"""
    communicate = Communicate(TEXT, VOICE,rate="+50%",volume="+50%")
    submaker = edge_tts.SubMaker()
    with open(OUTPUT_FILE, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

    with open(WEBVTT_FILE, "w", encoding="utf-8") as file:
        file.write(submaker.generate_cn_subs(TEXT))


loop = asyncio.get_event_loop_policy().get_event_loop()
try:
    loop.run_until_complete(amain())
finally:
    loop.close()
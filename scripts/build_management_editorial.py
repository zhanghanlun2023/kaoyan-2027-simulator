"""Build complete 199 papers with long materials and intact multi-question groups."""

from __future__ import annotations

import json
import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "data" / "questions_199.json"
LETTERS = "ABCDE"
CS_OPTIONS = {
    "A": "条件（1）充分，但条件（2）不充分",
    "B": "条件（2）充分，但条件（1）不充分",
    "C": "条件（1）和（2）单独都不充分，但联合起来充分",
    "D": "条件（1）充分，条件（2）也充分",
    "E": "条件（1）和（2）单独都不充分，联合起来也不充分",
}


def optionize(correct, distractors, seed):
    values = list(dict.fromkeys([str(correct), *map(str, distractors)]))
    if len(values) != 5:
        raise ValueError(values)
    random.Random(seed).shuffle(values)
    options = dict(zip(LETTERS, values))
    answer = next(key for key, value in options.items() if value == str(correct))
    return options, answer


def add(bank, paper, order, chapter, stem, options, answer, points, explanation, *, group_id=None, shared_stem=None, qtype="single"):
    bank.append({
        "id": f"199_{paper}_{order:02d}", "paper_id": f"199_editorial_{paper}", "paper_order": order,
        "subject": "管理类综合能力", "chapter": chapter, "type": qtype, "stem": stem,
        "options": options, "answer": answer, "points": points, "difficulty": 3 + order % 2,
        "explanation": explanation, "source": "原创仿真·真题结构重建", "format_tag": "199完整仿真卷",
        "group_id": group_id, "shared_stem": shared_stem,
    })


def number_options(correct, paper, order, spread=1):
    if isinstance(correct, float) and not correct.is_integer():
        candidates = [correct, correct - spread, correct + spread, correct - 2 * spread, correct + 2 * spread]
        values = [f"{x:.2f}".rstrip("0").rstrip(".") for x in candidates]
    else:
        correct = int(correct)
        values = [correct, correct - spread, correct + spread, correct - 2 * spread, correct + 2 * spread]
    return optionize(str(values[0]), [str(x) for x in values[1:]], paper * 100 + order)


LOGIC_CONTEXTS = [
    ("市图书馆延长周末开放时间", "周末到馆人数上升", "同期附近两所自习室暂停营业"),
    ("社区医院发送复诊提醒", "爽约率下降", "试点科室同时缩短了候诊时间"),
    ("制造企业实行班前安全复盘", "轻微事故报告增加", "新制度鼓励员工主动上报险情"),
    ("高校开放课程录像", "期末平均分提高", "选择观看录像的学生原本学习投入更高"),
    ("商场设置可回收包装点", "回收量快速增长", "活动期间每次回收都可兑换积分"),
    ("公交公司公布实时到站信息", "乘客满意度提高", "同一时期线路准点率也明显改善"),
    ("出版社提供样章试读", "退书率下降", "试读用户更倾向购买熟悉作者的作品"),
    ("企业试行四天项目周期", "团队按期交付率提高", "试点团队获得了额外技术支持"),
    ("博物馆重写展品说明", "访客停留时间延长", "新展览本身包含更多互动装置"),
    ("银行简化开户表格", "一次填写成功率提高", "试点网点增加了现场引导人员"),
    ("城市公园增加遮阴座椅", "午间访客增加", "试点月份平均气温低于往年"),
    ("在线平台提前说明退改规则", "付款完成率提高", "平台同期推出了限时价格优惠"),
    ("职业学校增加项目式训练", "毕业生就业率提高", "当地制造业同期扩大招聘规模"),
    ("物业向住户发送用能报告", "高峰用电下降", "试点小区同期更换了节能设备"),
    ("招聘网站展示薪酬区间", "有效申请比例提高", "参与企业同时提高了最低薪酬"),
    ("餐饮企业标注营养信息", "低热量菜品销量增加", "菜单同时将这些菜品移到首页"),
    ("慈善机构定期反馈项目进度", "小额捐赠复捐率提高", "收到反馈者本来就是活跃捐赠人"),
    ("档案馆上线数字检索目录", "远程查档申请增加", "同期取消了纸质目录邮寄服务"),
    ("物流公司缩小送达时间窗口", "首次投递成功率提高", "试点区域新增了自提柜"),
    ("酒店上线移动端入住", "前台排队时间缩短", "淡季入住人数本身较少"),
    ("研究机构预注册分析方案", "研究结论复现率提高", "参与团队还接受了统计培训"),
    ("社区中心开放线上预约", "课程出席率提高", "热门课程同时增加了名额"),
    ("新闻网站醒目标注更正记录", "读者信任度提高", "调查只覆盖长期订阅用户"),
    ("运动俱乐部提供灵活时段", "会员到场次数增加", "试点期间会员费有所下降"),
    ("电信公司使用图形化账单", "账单理解正确率提高", "受访者完成测试前接受了示例讲解"),
    ("培训平台提供即时练习反馈", "课程完成率提高", "新版本同时缩短了课程长度"),
    ("地方政府发布预算摘要", "公众政策理解度提高", "参与调查者教育程度高于总体"),
    ("住宅部门发送截止日期提醒", "按时提交率提高", "当期申请流程减少了两项材料"),
    ("诊所开放在线查询检验结果", "复诊完成率提高", "试点患者居住地离诊所更近"),
    ("旅游平台前置风险提示", "游客取消纠纷减少", "同一时期极端天气事件减少"),
    ("高校设置同伴写作辅导", "课程论文通过率提高", "主动报名者的基础成绩更好"),
    ("超市将健康食品放在视线高度", "相关商品销量提高", "这些商品同期进行了价格促销"),
    ("养老机构引入家属沟通平台", "投诉数量下降", "平台上线后投诉分类标准发生变化"),
    ("软件团队进行代码评审", "上线缺陷率下降", "试点项目的复杂度低于其他项目"),
    ("工厂引入预测性维护", "非计划停机减少", "试点设备刚完成过一次全面检修"),
    ("学校推行分阶段测验", "学生报告的焦虑下降", "课程同时取消了成绩排名"),
    ("政府热线统一工单分类", "平均处理时间缩短", "统计口径排除了转办等待时间"),
    ("医院推行电子用药核对", "处方差错减少", "试点病区药品种类相对较少"),
    ("企业公开内部岗位信息", "跨部门流动增加", "公司同期扩大了内部招聘名额"),
    ("景区实行分时预约", "入口拥堵缓解", "试点期间游客总量低于去年"),
    ("大学食堂公布拥挤指数", "错峰就餐比例提高", "部分课程的下课时间也被调整"),
    ("保险公司简化理赔说明", "材料补交次数下降", "客服同期增加了主动回访"),
    ("公共自行车增加维护频次", "故障投诉下降", "同期淘汰了一批老旧车辆"),
    ("公司采用匿名意见渠道", "员工建议数量增加", "新制度将被采纳建议与奖金挂钩"),
    ("学校为新生提供导航地图", "迟到比例下降", "新学期多数课程集中在同一教学区"),
    ("零售商提供维修指南", "轻微故障退货减少", "使用指南者通常具备更强动手能力"),
    ("实验室共享设备日历", "设备闲置率下降", "同期新增项目提高了总体使用需求"),
    ("居民区设置厨余分类督导", "分类准确率提高", "督导期间违规行为会被公开提醒"),
    ("大学开放跨院选课", "课程满意度提高", "样本只包含成功选到理想课程者"),
    ("客服中心使用知识库", "首次解决率提高", "资深员工被优先安排到试点班次"),
    ("城市上线积水预警", "暴雨出行损失下降", "试点年份降雨强度低于历史平均"),
    ("企业设置无会议时段", "深度工作时间增加", "试点部门同时减少了项目数量"),
    ("大学提供实验预习视频", "实验操作错误减少", "观看者可以重复参加线上测试"),
    ("农贸市场公示检测结果", "消费者购买信心提高", "调查在食品安全宣传周内进行"),
]


def add_math(bank, paper):
    p = paper
    cases = []
    v1, v2, v3 = 12 + p, 18 + p, 15 + p
    correct = round(3 / (1 / v1 + 1 / v2 + 1 / v3), 2)
    cases.append((f"某人全程分为等长的三段，速度依次为{v1}、{v2}、{v3}千米/时。若中途不停留，则全程平均速度为多少千米/时？", correct, 1, "等长路段应以总路程除以总时间，不能直接取速度算术平均。"))
    a, ab, abc = 12 + p, 5 + p, 3 + p
    remain = 1 - (1 / abc - 1 / ab)
    days = round(remain / (1 / ab), 2)
    cases.append((f"甲独做一项工程需{a}天，甲乙合作需{ab}天，甲乙丙合作需{abc}天。丙先单独工作1天，余下由甲乙合作，需要多少天？", days, 1, "先用合作效率之差求丙的效率，再计算剩余工作量。"))
    total = 1800 + p * 300
    cases.append((f"某公司年度红利的20%由三位股东平均分配，其余按2∶3∶5的持股比例分配。若持股最少者最终分得{round(total*.2/3+total*.8*.2)}万元，则红利总额为多少万元？", total, 300, "最少股东所得=平均分配部分的1/3+按股权分配部分的2/10。"))
    union = 72 + p
    both = 18 + p
    first = 48 + p
    second = union - first + both
    cases.append((f"某单位{union+12}名员工中有12人未参加比赛；参加田赛的有{first}人，田赛和径赛都参加的有{both}人。参加径赛的员工有多少人？", second, 2, "使用容斥原理：田赛+径赛-两项都参加=至少参加一项。"))
    r, b, k = 2+p, 4+p, 3+p
    same = (math.comb(r,2)+math.comb(b,2)+math.comb(k,2))/math.comb(r+b+k,2)
    cases.append((f"袋中有{r}个红球、{b}个蓝球和{k}个黑球，随机不放回取2个球，取到同色球的概率为多少？", round(same,3), .05, "用同色组合数之和除以全部两球组合数。"))
    n = 30 + 3*p
    pattern_sum = sum(i if i%3 else -i for i in range(1,n+1))
    cases.append((f"计算1+2-3+4+5-6+…+{n-2}+{n-1}-{n}的值。", pattern_sum, 3, "每三项为一组求和，再累加各组结果。"))
    left, right = 2+p, 3+p
    ways = math.comb(left+right,left)
    cases.append((f"两组集装箱分别自上而下有{left}箱和{right}箱，每次只能运走某组最上面的一箱。将全部集装箱运走共有多少种不同顺序？", ways, 2, "保持每组内部顺序不变，只需选择第一组箱子在总序列中的位置。"))
    base, up, down = 200+20*p, 20+p, 10+p
    value = base*(1+up/100)*(1-down/100)
    cases.append((f"某商品原价{base}元，先上涨{up}%，再在新价格基础上下降{down}%。最终价格为多少元？", round(value,2), 5, "两次百分比变化的基数不同，应连续相乘。"))
    c1,c2,target = 20+p, 50+p, 35+p
    ratio = round((target-c1)/(c2-target),2)
    cases.append((f"将浓度为{c1}%与{c2}%的两种溶液混合成浓度{target}%的溶液，前者与后者的质量比为多少？", ratio, .25, "按浓度差的反比计算两种溶液质量比。"))
    cases.append((f"某课程平时成绩占40%，期末成绩占60%。一名学生平时成绩为{72+p}分，若总评需达到{80+p}分，期末至少应得多少分？", round(((80+p)-.4*(72+p))/.6,2), 2, "建立加权平均方程求期末成绩。"))
    cases.append((f"正整数x、y满足x+y={19+2*p}且x<y。要使xy最大，x应取多少？", (19+2*p)//2, 1, "和固定时两数越接近乘积越大，并结合整数与大小限制。"))
    cases.append((f"从{7+p}名候选人中选3人组成小组，且甲、乙两人不能同时入选，共有多少种选法？", math.comb(7+p,3)-math.comb(5+p,1), 3, "总选法减去甲乙同时入选时再选1人的选法。"))
    length,width = 8+p,5+p
    cases.append((f"长方形周长为{2*(length+width)}，长比宽多{length-width}。连接两条对角线，其交点到一条长边的距离为多少？", width/2, .5, "先由和差求长宽；对角线交点为中心，到长边距离为宽的一半。"))
    father, child = 38+p, 10+p
    t = (father-3*child)/2
    cases.append((f"父亲今年{father}岁，孩子今年{child}岁。多少年前父亲年龄是孩子年龄的3倍？", t, 1, "设t年前满足父亲年龄减t等于孩子年龄减t的3倍。"))
    cost, fixed, target_profit = 60+2*p, 600+50*p, 1800+100*p
    price = 90+2*p
    qty = math.ceil((fixed+target_profit)/(price-cost))
    cases.append((f"某产品单位变动成本{cost}元，售价{price}元，每期固定成本{fixed}元。要使利润不少于{target_profit}元，至少销售多少件？", qty, 5, "利润=销量×单位贡献-固定成本，列不等式并向上取整。"))
    for order,(stem,correct,spread,exp) in enumerate(cases,1):
        options,answer=number_options(correct,paper,order,spread)
        add(bank,paper,order,"数学基础·问题求解",stem,options,answer,3,exp)


def add_sufficiency(bank, paper):
    rows = [
        ("能确定实数x的值", f"（1）x+y={12+paper}；\n（2）x-y={2+paper}", "C", "两个独立方程联合可唯一确定x，单独均不能。"),
        ("能确定正整数n的值", f"（1）n是{6+paper}的倍数且n<{12+2*paper}；\n（2）n为偶数", "A", "条件（1）把正整数限制为唯一倍数，条件（2）不能。"),
        ("能确定三角形的面积", f"（1）底边长为{8+paper}；\n（2）该底边上的高为{5+paper}", "C", "底和对应高联合才能确定面积。"),
        ("能确定两正整数a、b的乘积", f"（1）a、b的最大公约数为{2+paper}；\n（2）a、b的最小公倍数为{18+3*paper}", "C", "对正整数有ab=最大公约数×最小公倍数。"),
        ("能确定等差数列的第10项", f"（1）首项为{2+paper}；\n（2）前5项和为{30+5*paper}", "C", "首项与前5项和联合可求公差。"),
        ("能确定圆的半径", f"（1）圆的面积为{(3+paper)**2}π；\n（2）圆的周长为{2*(3+paper)}π", "D", "任一条件都能单独确定正半径。"),
        ("能确定某班平均成绩", f"（1）全班总分为{2400+100*paper}；\n（2）全班人数为{30+paper}", "C", "平均数需要总分与人数两个信息。"),
        ("能确定实数x是否大于0", "（1）x²>0；\n（2）x³>0", "B", "平方为正只能说明非零；立方为正等价于x为正。"),
        ("能确定长方形的面积", f"（1）周长为{30+2*paper}；\n（2）对角线长为{13+paper}", "C", "由长宽和与平方和联合可求乘积；单独均有多解。"),
        ("能确定一元二次方程有两个不同实根", f"（1）判别式大于0；\n（2）两根之和为{5+paper}", "A", "判别式大于0直接充分；根和不能判断根是否存在且不同。"),
    ]
    for idx,(goal,conditions,answer,exp) in enumerate(rows,16):
        add(bank,paper,idx,"数学基础·条件充分性判断",f"判断以下条件能否充分支持结论：{goal}。\n{conditions}",CS_OPTIONS,answer,3,exp)


def add_logic_singles(bank, paper):
    start=(paper-1)*18
    question_types=["weaken","strengthen","assumption","explain","flaw","inference"]*3
    for offset,kind in enumerate(question_types):
        topic,outcome,alternative=LOGIC_CONTEXTS[start+offset]
        material=(f"某机构对“{topic}”进行了为期八周的试点，并将试点前后的业务数据进行比较。结果显示，{outcome}。"
                  f"项目负责人据此断言，这一变化主要由该措施造成，因此应立即在全部单位推广。评估人员提醒，观察期内还发生了其他变化，"
                  f"样本的参与方式也可能影响结论，而且短期指标未必等同于长期效果。")
        neutral=["该措施的实施成本处于预算范围内","多数参与者表示愿意继续参加","其他地区过去也讨论过类似措施","项目报告采用了图表展示结果"]
        if kind=="weaken":
            stem="以下哪项如果为真，最能削弱项目负责人的结论？"; correct=alternative; exp="该信息给出了与措施同时发生、足以解释结果的替代原因。"
        elif kind=="strengthen":
            stem="以下哪项如果为真，最能加强项目负责人的结论？"; correct=f"在排除“{alternative}”影响后，试点组相对匹配对照组仍出现同方向显著变化"; exp="控制替代解释且保留组间差异，增强了因果解释。"
        elif kind=="assumption":
            stem="项目负责人的论证最需要以下哪项作为假设？"; correct="试点前后指标口径一致，且参与者构成变化不足以单独造成观察结果"; exp="若测量口径或样本构成改变，前后比较不能支持因果结论。"
        elif kind=="explain":
            stem="以下哪项最能解释试点结果而又不支持立即全面推广？"; correct=f"措施只对原先面临特定障碍的一小类参与者有效，而该类人在试点样本中的比例特别高"; exp="它解释局部改善，同时限制结论的外推范围。"
        elif kind=="flaw":
            stem="上述论证存在的主要问题是？"; correct="把试点前后的相关变化直接解释为措施造成，并把短期局部结果外推到全部单位"; exp="论证同时存在因果跳跃与样本外推问题。"
        else:
            stem="根据以上材料，以下哪项是最稳妥的推断？"; correct="现有结果足以支持进一步扩大验证，但不足以单独证明普遍、长期的因果效果"; exp="该结论既保留证据价值，也不超出试点设计的证明范围。"
        options,answer=optionize(correct,[*neutral[:3],f"只要{outcome}，任何单位都应采用该措施"],paper*1000+offset)
        add(bank,paper,26+offset,"逻辑推理",material+"\n\n"+stem,options,answer,2,exp)


GROUP_SETTINGS = [
    ("城市更新听证会", ["甲主张先改善公共交通再限制私家车", "乙认为低收入者目前难以承担替代交通成本", "丙认为不能立即限车就是忽视空气污染", "丁指出历史排放较高的行业应承担更多成本", "戊主张若要求居民改变出行方式，政府必须先提供可靠公交", "己认为污染模型仍有误差，不宜采取高成本措施"]),
    ("企业数字化评审会", ["甲主张所有部门立即采用统一系统", "乙指出小型部门缺少迁移数据的能力", "丙认为不立即统一就是拒绝效率提升", "丁强调过去系统债务主要由总部决策形成", "戊主张总部若要求统一就必须提供培训和迁移预算", "己认为收益估计仍不确定，不宜一次投入全部预算"]),
    ("校园空间调整讨论", ["甲主张减少停车位并扩大学习空间", "乙指出通勤学生目前缺少替代出行方式", "丙认为反对立即调整就是不重视学习环境", "丁认为过去规划偏向车辆，校方应优先纠正", "戊主张调整前必须增加校车班次", "己认为使用率数据不完整，不宜立即重建"]),
]


def add_logic_groups(bank,paper):
    base=44
    views="\n".join(GROUP_SETTINGS[paper-1][1])
    shared=f"【公共材料一：{GROUP_SETTINGS[paper-1][0]}】\n围绕一项资源配置方案，六位代表依次发表意见：\n{views}\n请只依据上述观点之间的支持、反驳和条件关系回答问题。"
    qs=[("以下哪项最准确地描述了观点关系？",{"A":"乙直接否定了甲的目标","B":"戊为甲的主张补充了实施条件","C":"丙为己的不确定性判断提供支持","D":"丁证明了甲的方案必然成功","E":"己与乙都主张永远维持现状"},"B","戊接受目标方向，但为实施补充必要前提。"),("若要加强戊的观点，最需要补充哪项？",{"A":"可靠替代条件不足会使受影响者承担不成比例的成本","B":"所有代表都喜欢当前方案","C":"历史上从未讨论过该问题","D":"任何改革都会产生争议","E":"数据误差可以被完全忽略"},"A","该项建立了前置支持与公平实施之间的联系。"),("以下哪项是材料中没有得到支持的推断？",{"A":"部分代表认可目标但质疑实施速度","B":"责任分配与现实能力是争论焦点","C":"六位代表一致反对改变现状","D":"不确定性被用来反对高成本立即行动","E":"政策条件可能影响观点是否成立"},"C","材料存在支持行动的观点，不可能推出一致反对。")]
    for i,(stem,opts,ans,exp) in enumerate(qs): add(bank,paper,base+i,"逻辑推理",stem,opts,ans,2,exp,group_id=f"199_{paper}_g1",shared_stem=shared)

    names=["甲","乙","丙","丁","戊","己"]
    shared=f"【公共材料二：项目排期】\n某机构要把{''.join(names)}六个项目安排在周一至周六，每天一个。已知：甲早于丁且两者不相邻；乙紧接在戊之后；丙不在周一或周六；己安排在丙之后；周三安排的不是甲也不是乙。请据此回答以下问题。"
    qs=[("以下哪项安排可能成立？",{"A":"周一丙、周二己","B":"周一戊、周二乙","C":"周三甲、周四丁","D":"周五戊、周六丙","E":"周一丁、周六甲"},"B","戊乙相邻且其余条件可继续满足。"),("若丙安排在周四，则以下哪项一定成立？",{"A":"己在周五或周六","B":"甲在周一","C":"乙在周三","D":"丁在周六","E":"戊在周二"},"A","己必须晚于周四，只能在周五或周六。"),("若甲安排在周二，则以下哪项不可能成立？",{"A":"丁在周四","B":"丁在周五","C":"丁在周六","D":"丙在周一","E":"戊在周三"},"D","丙明确不能安排在周一。")]
    for i,(stem,opts,ans,exp) in enumerate(qs): add(bank,paper,base+3+i,"逻辑推理",stem,opts,ans,2,exp,group_id=f"199_{paper}_g2",shared_stem=shared)

    courses=["财务","运营","营销","战略","数据","组织"]
    shared=f"【公共材料三：课程选择】\n某班从{''.join(courses)}六门模块中选择三门组成训练周。规则如下：财务与数据至少选一门但不能同时选择；若选营销则必须选战略；运营与组织不能同时选择；选择数据时必须同时选择运营；任何方案都恰好选择三门。"
    qs=[("以下哪项选择方案符合全部规则？",{"A":"财务、营销、战略","B":"财务、运营、组织","C":"数据、运营、组织","D":"数据、营销、战略","E":"财务、数据、战略"},"A","A满足互斥、蕴含和数量要求。"),("若选择数据，则以下哪项一定被选择？",{"A":"财务","B":"运营","C":"营销","D":"战略","E":"组织"},"B","规则直接规定数据推出运营。"),("若选择组织且不选择营销，则第三门之外必然包含哪门？",{"A":"财务","B":"运营","C":"数据","D":"战略","E":"营销"},"A","组织排除运营，数据又要求运营，因此只能选择财务满足财务/数据规则。")]
    for i,(stem,opts,ans,exp) in enumerate(qs): add(bank,paper,base+6+i,"逻辑推理",stem,opts,ans,2,exp,group_id=f"199_{paper}_g3",shared_stem=shared)

    shared=f"【公共材料四：质量复核】\n某团队复核A、B、C、D、E五份报告，每份由一名分析员和一名审核员负责。甲、乙、丙三人担任分析员，丁、戊担任审核员。已知：甲至少分析两份；乙不分析A；丙分析D；丁不审核甲分析的报告；A与D由不同审核员审核；每份报告只安排一次分析和一次审核。"
    qs=[("若A由甲分析，则A由谁审核？",{"A":"甲","B":"乙","C":"丙","D":"丁","E":"戊"},"E","丁不能审核甲分析的报告，因此只能由戊审核。"),("以下哪项安排一定违反规则？",{"A":"乙分析B","B":"丙分析D","C":"丁审核乙分析的报告","D":"丁审核甲分析的报告","E":"戊审核A"},"D","规则明确禁止丁审核甲分析的报告。"),("若D由丁审核，则以下哪项一定成立？",{"A":"A由戊审核","B":"A由甲分析","C":"B由乙分析","D":"C由丙分析","E":"E由丁审核"},"A","A和D审核员不同，审核员只有丁、戊，因此A必由戊审核。")]
    for i,(stem,opts,ans,exp) in enumerate(qs): add(bank,paper,base+9+i,"逻辑推理",stem,opts,ans,2,exp,group_id=f"199_{paper}_g4",shared_stem=shared)


WRITING_ARGUMENTS = [
    "某公司认为，只要把所有决策都交给数据模型，管理效率就一定提高。因为模型不会受到情绪影响，所以模型的结论必然客观；客观结论自然能够得到员工支持。员工一旦支持，执行成本就会下降，利润也会随之增长。即使模型偶尔出错，也只是因为输入数据不足，只要继续收集数据，任何管理问题最终都能被模型解决。因此，公司应立即取消各部门的人工复核岗位，并把节省的费用全部用于购买更多数据。",
    "某城市提出，只要建设更多大型文化场馆，居民文化素养就会显著提升。场馆数量增加意味着文化资源增加，文化资源增加必然带来更高的使用率；使用率提高又说明居民已经获得了更好的文化教育。既然一些知名城市拥有许多大型场馆并且经济发达，本市复制这种做法也一定能够促进经济增长。即便目前部分场馆利用率不高，也只是宣传不足，只要增加广告投入便可解决。因此应压缩社区小型文化项目，把资金集中用于建设地标场馆。",
    "某高校认为，课程录像观看次数与考试成绩呈正相关，因此增加录像数量必然能够提高所有学生的成绩。成绩提高会增强学习兴趣，学习兴趣增强又会进一步增加观看次数，从而形成持续提升。既然录像可以反复播放，教师课堂讲解就变得不再必要；取消大班授课还可以降低教学成本。即使有学生不主动观看，也可以通过强制打卡解决。因此学校应把绝大多数课程改成录像自学，并用观看时长代替平时成绩。",
]


def add_writing(bank,paper):
    material=WRITING_ARGUMENTS[paper-1]
    add(bank,paper,56,"写作·论证有效性分析",f"分析下述论证中存在的缺陷和漏洞，选择若干要点，写一篇600字左右的文章，对论证的有效性进行分析和评述。\n\n{material}",{},"人工自评",30,"自评重点：识别概念混淆、因果跳跃、样本类比、必要条件与充分条件混用，以及结论超出论据范围。",qtype="essay")
    prompts=["有人认为，真正有效的合作不是消除分歧，而是让不同意见在共同规则下接受检验。请结合实际，写一篇700字左右的论说文。","一项选择的价值，不只取决于它带来的即时收益，也取决于它为未来保留了多少调整空间。请结合实际，写一篇700字左右的论说文。","评价一个组织是否进步，既要看它解决了多少旧问题，也要看它是否具备发现新问题、修正自身的能力。请结合实际，写一篇700字左右的论说文。"]
    add(bank,paper,57,"写作·论说文",prompts[paper-1],{},"人工自评",35,"自评重点：立意明确；概念界定清楚；论据与论点关联紧密；包含必要的反方回应或边界条件；结构完整。",qtype="essay")


def build_management_bank():
    bank=[]
    for paper in range(1,4):
        add_math(bank,paper); add_sufficiency(bank,paper); add_logic_singles(bank,paper); add_logic_groups(bank,paper); add_writing(bank,paper)
    for paper in range(1,4):
        rows=[q for q in bank if q["paper_id"]==f"199_editorial_{paper}"]
        assert len(rows)==57 and sum(q["points"] for q in rows)==200
        assert len([q for q in rows if q["chapter"]=="逻辑推理"])==30
        groups={q["group_id"] for q in rows if q.get("group_id")}
        assert len(groups)==4 and all(sum(q.get("group_id")==g for q in rows)==3 for g in groups)
    return bank


if __name__ == "__main__":
    payload=build_management_bank()
    TARGET.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"papers":3,"questions":len(payload),"per_paper":57},ensure_ascii=False))


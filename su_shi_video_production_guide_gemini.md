# 零基础使用 WorkBuddy 制作《苏轼一生》系列短视频全指南

** WorkBuddy** 是一个出色的 AI 协同工具，不仅能处理日常办公，还能通过“专家团”或自定义 Agent 模式将复杂的视频生成流程（文案、分镜、配音、合成）自动化。

对于只有基础 AI 经验的新手，制作一套**《苏轼一生》系列史诗短视频**是非常棒的项目。建议采用 **“WorkBuddy 负责流程编排与自动化 + 专业大模型辅助精细化生成”** 的工作流，无需陷入繁琐的底层细节。

---

## 一、 学习路线图：核心能力储备

作为项目的“总导演”，你不需要成为编程专家或专业剪辑师，重点掌握以下 4 种核心能力：

```
[知识储备] 苏轼历史资料与词作整理
   ↓
[文案与分镜] 用 WorkBuddy 编写系列剧本 & 结构化 Prompt
   ↓
[视觉一致性] 角色定型 (IP) 与 场景/美学风格统一
   ↓
[合成与剪辑] WorkBuddy 自动化渲染 / 剪映后期微调
```

1. **结构化 Prompt 撰写能力**：学会用“角色 + 背景 + 格式要求”引导 WorkBuddy 输出标准的分镜表。
2. **AI 视觉一致性技巧**：掌握如何让苏轼从青年到老年“长同一张脸”（一致性控制）。
3. **语音音色匹配与情感**：为苏轼不同人生阶段挑选契合的 AI 声音（如：青年意气风发、晚年豁达沉郁）。
4. **自动化与剪辑基础**：了解 WorkBuddy 导出/渲染机制，以及用剪映进行简单的音画同步调整。

---

## 二、 零基础落地 SOP：从零到一制作《苏轼一生》

为了让长达数十年的苏轼生涯有条不紊地呈现，建议先规划**分集结构**（如：*第1集：黄州赤壁·浴火重生*；*第2集：密州出猎·左牵黄右擎苍* 等）。

以制作 **《第一集：黄州赤壁（乌台诗案后的蜕变）》** 为例：

### 阶段一：脚本与分镜设计（WorkBuddy 自动化）
直接在 WorkBuddy 输入结构化指令，调用文案与策划能力：

> **给 WorkBuddy 的提示词模板：**
> 
> “你现在是《苏轼传》纪录片的主编剧。请帮我编写第一集《黄州赤壁》的短视频脚本，时长约 60 秒。
> 请输出为表格格式，包含：`镜号`、`时间`、`画面描述（含宋代服饰与环境细节）`、`配音旁白（包含《念奴娇·赤壁怀古》名句）`、`AI生图Prompt（英文，写实国风/国画写实风格）`。”

### 阶段二：人物与画面设计（解决一致性）
为了防止每张图里的苏轼“换脸”，先定稿一套**角色基准卡**：

1. **美学风格**：统一设定为 *`Chinese ink style, Song Dynasty aesthetic, realistic watercolor, cinematic lighting`*（宋代美学、水墨写实、电影光影）。
2. **角色设定（老年/黄州时期）**：*`A middle-aged Song Dynasty scholar, wearing a traditional dark robe and scholar hat, with a sparse beard, resilient and peaceful expression.`*
3. **生图策略**：
   * 在 WorkBuddy 关联的生图模型（或豆包/Midjourney/Kling）中生成首张满意的人像。
   * 锁定该人像作为 **垫图/参考图 (Image Prompt)**，后续所有镜头均带上此参考图或一致性 Seed 码。

### 阶段三：音频与配音（TTS 音色挑选）
1. **旁白音色**：选择沉稳、有讲故事感的中文男声（如 Azure TTS 中的 `zh-CN-YunxiNeural` 或 `zh-CN-YunzeNeural` 等沉静男声）。
2. **配乐（BGM）**：选择古筝、箫、埙为主的中国古典民乐（建议前半段抑郁低沉，后半段豁达大气）。

### 阶段四：图生视频与合成（WorkBuddy / Kling / Runway）
1. **图生视频**：将生成的静态分镜图片送入视频大模型（如 Kling、Runway 或 WorkBuddy 内置的模型），加上微动提示词（如：`wind blowing robe, river flowing smoothly, slow zoom in`，微风吹拂长袍、江水东流、镜头缓慢拉近）。
2. **自动化渲染/一键成片**：
   * **方法 A（WorkBuddy 极简模式）**：将整理好的文案、图文素材直接输入 WorkBuddy 视频生成插件/专家团，让其自动拼装字幕、配音与画面。
   * **方法 B（精细剪辑模式）**：下载所有视频片段与 TTS 配音包，导入剪映，按 WorkBuddy 给出的时间轴对齐即可。

---

## 三、 剧本与分镜示例表（第1集片段）

| 镜号 | 时间 | 画面描述 | 配音旁白 | 生图 Prompt 关键词 |
| :--- | :--- | :--- | :--- | :--- |
| **01** | 0-4s | 夜晚，大江东去，月光洒在惊涛拍岸的江面上 | 大江东去，浪淘尽，千古风流人物。 | *Song Dynasty Red Cliff, night, moonlight on turbulent Yangtze river, masterpiece, Chinese dark mood painting.* |
| **02** | 4-10s | 苏轼身穿青灰色粗布长衫，独坐江边小舟，手执酒杯，神情从凝重转为释然 | 那一年，乌台诗案爆发，他身陷囹圄，险些丧命。被贬黄州后，他在这里写下了旷世绝唱。 | *Middle-aged Chinese scholar in dark Song robe sitting on a small wooden boat, holding a wine cup, peaceful look, ultra-detailed.* |
| **03** | 10-15s | 镜头特写：苏轼在简陋的东坡雪堂挥毫泼墨，提笔写下“竹杖芒鞋轻胜马，谁怕？一蓑烟雨任平生” | 从“苏轼”到“东坡居士”，黄州没有消磨他的意志，反而成就了他的豁达与超脱。 | *Close-up of a scholar calligraphy in a humble cottage, ink splashing, cinematic sunlight breaking through soft fog.* |

---

## 四、 避坑指南与进阶建议

1. **避免信息量过载**：苏轼一生极为丰富，**切忌一集讲完**。建议按“人生的关键节点”拆成 5-8 集短视频（例如：①京城惊艳出世 ②密州与徐州 ③乌台诗案 ④黄州赤壁 ⑤惠州与儋州晚年）。
2. **文字敏感词与史实校验**：利用 WorkBuddy 的文本处理能力，在脚本生成后输入“*请检查脚本中是否有历史史实错误或敏感违规词*”，提升脚本专业度。
3. **美学风格保持单一**：全集切忌一会儿用水墨国风，一会儿用 3D 动漫风。**确定一套国风水墨/写实宋韵提示词后，全文复用**。
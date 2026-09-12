# KRCIGE：一个有界工程框架

从认识有限（K）、资源有限（R）、控制有限（C）与工程不可逆性（I）四个描述性要素，加上工程目标（G）、伦理边界（E）与反馈适用结构条件 Σ，构造面向软件工程行动的条件性解释与决策框架。

当前为理论化修订 v0.3，内容包括：

- 统一的工程情境、策略级风险约束与可行策略模型
- 与软件工程经济学、实物期权、恢复计算、系统安全及经验理论研究的关系
- 任务相关恢复成本、事前信息价值命题及 I 与技术债务的概念区分
- 十三条中间原则的机制、成本、指标及失效边界
- 利益相关者、风险承担与跨团队、跨时间的目标和约束
- `examples/sequential_release.py` — 合成输入的精确递推、11 组敏感性场景与独立树展开自检
- 拟开展的独立评估、基线比较、原则消融和决策辅助效果研究
- 以 *The Pragmatic Programmer* 100 条 Tips 和 Twelve-Factor App 展示解释性对应
- 中文学术期刊通用的 A4 单栏排版：标题页、关键词、页眉页码、编号公式与附录分流

## 文件

- `krcige_bounded_engineering_draft.tex` — LaTeX 源文件（ctexart，需 XeLaTeX 编译）
- `krcige_bounded_engineering_draft.pdf` — 编译好的 PDF
- `examples/sequential_release.py` — 可复现的序贯发布数值示例

论文源文件中的作者、单位和电子邮箱目前保留为待填字段；正式投稿前请替换为实际署名信息。

目前的证据限于条件命题、合成计算与文本映射，尚未完成独立前瞻性预测或因果效果评估。数值案例使用已有的贝叶斯决策和动态规划方法，演示模型内的策略边界；它不证明 KRCIGE 优于使用相同信息的其他决策方法。

## 编译

```bash
xelatex krcige_bounded_engineering_draft.tex
xelatex krcige_bounded_engineering_draft.tex
python examples/sequential_release.py
python examples/sequential_release.py --sensitivity
```

（LaTeX 编译两遍以更新公式、表格和交叉引用；Python 脚本只使用标准库。默认输出基准案例，`--sensitivity` 比较不观察、最多一轮和最多两轮的决策值，并检查观察、扩大和停止的策略反转。）

## 许可

[CC BY-NC-SA 4.0](LICENSE)

# KRCIGE：一个有界工程框架

从认识有限（K）、资源有限（R）、控制有限（C）与工程不可逆性（I）四个描述性要素，加上工程目标（G）、伦理边界（E）与可学习结构条件 Σ，构造面向软件工程行动的情境化序贯决策理论。

当前为理论化修订 v0.2，内容包括：

- 统一的工程情境与可行策略模型
- K、R、C、I 的量化定义及工程不可逆性区分命题
- 十三条中间原则的机制、指标、方向与边界
- 机制层压缩、原则消融与序贯发布递推
- `examples/sequential_release.py` — 合成输入的精确有限时域后向递推与自检
- 跨材料独立评估、基线比较与结果复现协议
- 以 *The Pragmatic Programmer* 100 条 Tips 和 Twelve-Factor App 展示覆盖与前瞻性使用
- 中文学术期刊通用的 A4 单栏排版：标题页、关键词、页眉页码、编号公式与附录分流

## 文件

- `krcige_bounded_engineering_draft_v0_1.tex` — LaTeX 源文件（ctexart，需 XeLaTeX 编译）
- `krcige_bounded_engineering_draft_v0_1.pdf` — 编译好的 PDF
- `examples/sequential_release.py` — 可复现的序贯发布数值示例

论文源文件中的作者、单位和电子邮箱目前保留为待填字段；正式投稿前请替换为实际署名信息。

## 编译

```bash
xelatex krcige_bounded_engineering_draft_v0_1.tex
xelatex krcige_bounded_engineering_draft_v0_1.tex
python examples/sequential_release.py
```

（LaTeX 编译两遍以更新公式、表格和交叉引用；Python 脚本只使用标准库并输出序贯递推结果。）

## 许可

[CC BY-NC-SA 4.0](LICENSE)

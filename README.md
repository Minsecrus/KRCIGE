# KRCIGE：一个有界工程框架

从认识有限（K）、资源有限（R）、控制有限（C）与工程不可逆性（I）四个描述性要素，加上工程目标（G）、伦理边界（E）与可学习结构条件 Σ，推导并解释软件工程经验原则（DRY、低耦合、小步迭代、版本控制、自动化测试等）的探索性框架。

当前为初稿 v0.1，内容包括：

- 四加二要素与 Σ 条件的定义
- 十三条中间原则及其派生关系
- 可复算的发布案例
- 以 *The Pragmatic Programmer* 100 条 Tips 检查压缩能力
- 用 Twelve-Factor App 做内部前瞻性留出核验

## 文件

- `krcige_bounded_engineering_draft_v0_1.tex` — LaTeX 源文件（ctexart，需 XeLaTeX 编译）
- `krcige_bounded_engineering_draft_v0_1.pdf` — 编译好的 PDF

## 编译

```bash
xelatex krcige_bounded_engineering_draft_v0_1.tex
xelatex krcige_bounded_engineering_draft_v0_1.tex
```

（编译两遍以生成目录。）

## 许可

[CC BY-NC-SA 4.0](LICENSE)
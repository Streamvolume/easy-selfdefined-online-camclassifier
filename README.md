# 自定义类别识别器

基于迁移学习的浏览器端实时多目标识别工具。使用 MobileNet 提取图像特征，结合 KNN 分类器实现自定义类别的即时训练与检测，无需服务器，所有推理在本地浏览器完成。

**[在线体验 →](https://streamvolume.github.io/easy-selfdefined-online-camclassifier/)**

![demo](https://img.shields.io/badge/TensorFlow.js-4.10-orange) ![demo](https://img.shields.io/badge/MobileNet-V2-blue) ![demo](https://img.shields.io/badge/license-MIT-green)

---

## 工作原理

```
摄像头 / 图片  →  MobileNet（特征提取，1280维向量）  →  KNN 分类器  →  多目标检测结果
```

MobileNet 作为冻结的特征提取骨干网络，KNN 作为轻量下游分类器。训练时只需采集少量样本（每类 ≥5 张），无需反向传播，即时生效。检测时对画面进行滑动窗口扫描，经 NMS 过滤后同时标注多个物体。

这是 [Google Teachable Machine](https://teachablemachine.withgoogle.com/) 的底层实现原理。

---

## 功能

- **自定义类别**：最多 8 个类别，名称可自由编辑
- **三种训练数据来源**：摄像头实时采集 / 框选区域采集 / 上传本地图片
- **多目标同时检测**：滑动窗口 + NMS，画面中同时标注多个物体
- **模型切换**：支持 MobileNet V2 1.0 / V2 0.5 / V1 1.0
- **KNN 持久化**：训练结果保存为 JSON，下次直接加载无需重新训练
- **离线模式**：通过 `setup.py` 下载 JS 库后完全离线运行

---

## 快速开始

### 在线使用

直接访问 GitHub Pages 链接，无需任何安装。

### 本地运行（支持离线）

```bash
# 克隆仓库
git clone https://github.com/Streamvolume/easy-selfdefined-online-camclassifier.git
cd custom-classifier

# 下载 JS 依赖库并启动本地服务器
python setup.py
```

按提示选择 `[1]` 下载依赖库，再选 `[2]` 启动服务器，浏览器会自动打开。

> Python 3.7+ 无需额外安装任何包，仅使用标准库。

---

## 使用说明

**训练**

1. 点击类别名称输入框，为每个类别命名
2. 选择采集方式：
   - **摄像头采集**：将物体对准摄像头，按住按钮连续抓帧
   - **框选采集**：在画面上拖拽画框，仅框内区域送入模型（推荐用于多目标场景）
   - **上传照片**：直接拖拽本地图片批量导入
3. 每类至少采集 5 个样本，点击「开始训练」

**检测**

训练完成后自动开始实时检测。调整底部滑块：
- **置信度阈值**：数值越高框越少但越准确，建议 50–70%
- **检测密度**：少/中/多 对应 5/14/22 个滑动窗口

**保存与加载**

- **保存 KNN**：将训练好的特征向量导出为 JSON，下次加载即可继续使用
- **保存模型到本地**：将 MobileNet 权重文件下载到本地，之后可离线加载

---

## 技术栈

| 组件 | 版本 | 用途 |
|------|------|------|
| TensorFlow.js | 4.10 | 浏览器端深度学习推理 |
| MobileNet | 2.1.0 | 图像特征提取骨干网络 |
| KNN Classifier | 1.2.4 | 轻量下游分类器 |

---

## 目录结构

```
├── index.html          # 主页面（即 custom-classifier-v3.html）
├── setup.py            # 本地环境管理脚本
├── libs/               # 本地 JS 库（由 setup.py 下载，gitignore 可选）
└── models/             # 本地模型权重（由浏览器「保存模型」功能生成）
    └── mobilenet_v2_1.0/
        ├── model.json
        └── model.weights.bin
```

---

## 许可证

MIT License

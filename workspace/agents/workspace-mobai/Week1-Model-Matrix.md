# AI设计总监·模型矩阵 v1

> 原则：高质量 × 高性价比 × 可自动化 × 可商业使用

---

## 1. 图像模型分层

### L1 日常探索层（便宜、快）
适用：方向探索、概念草图、构图预演、封面尝试
- `minimax/image-01`
- `deepinfra/black-forest-labs/FLUX-1-schnell`（待配置）
- `google/gemini-3.1-flash-image-preview`（待配置）

### L2 商业出图层（主力）
适用：营销图、配图、品牌概念图、KV
- `openai/gpt-image-2`（待配置）
- `google/gemini-3-pro-image-preview`（待配置）
- `fal-ai/flux/dev`（待配置）

### L3 高控制层（精修 / 一致性 / 批量延展）
适用：角色一致性、产品一致性、风格复用、局部重绘
- ComfyUI / ControlNet / LoRA（后续接入）
- fal image-to-image / ref-guided workflows

---

## 2. 视频模型分层

### V1 快速验证层
- MiniMax Hailuo 2.3
- BytePlus Seedance Lite
- Wan 2.6 / 2.7

### V2 商业主力层
- Runway Gen 4.5
- Google Veo 3.1 Fast / Standard
- Kling（via fal / together）

### V3 高规格项目层
- Veo 3.1 Standard
- Runway 高控制工作流
- Seedance Pro / Reference-to-Video

---

## 3. 选型原则

### Logo
优先：可控性 > 黑白识别 > 符号清晰 > 花哨质感
建议流程：
1. LLM先生成 logo brief
2. 图像模型只做“概念方向图”
3. 最终符号要人工收敛 / 向矢量化规范靠拢

### 海报/KV
优先：构图 > 情绪 > 品牌调性 > 文案可叠加性
建议：
- 概念探索用低成本层
- 终稿冲刺用商业主力层

### 产品图/宣传图
优先：材质 > 光影 > 边缘控制 > 一致性
建议：
- 先文生图
- 再图生图局部修正

### 视频
优先：关键帧质量 > 镜头运动 > 时长
建议：
- 先出关键帧
- 再做 4-8 秒镜头
- 长片靠剪辑拼接，不迷信单次长生成

---

## 4. 当前建议的最优先补齐顺序

1. **Google 图像/视频接口**：上限高，图+视频都能覆盖
2. **OpenAI gpt-image-2**：品牌海报、合成与编辑强
3. **fal**：统一接入 Flux / Seedance / Kling，适合自动化
4. **Runway**：视频商业交付核心
5. **ComfyUI**：后期做私有可控生产线

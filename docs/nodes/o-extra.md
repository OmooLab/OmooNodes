# O Extra 节点参考

本页收录 6 个资产节点，重点说明节点能做什么、参数如何影响结果，以及值得尝试的用法。

机器接口信息由 `node-catalog.json` 单独维护。同名输入属于不同模式时，会用「面板 / 参数」标明它所在的位置。

## 快速索引

- O Extra：`O Draw Shape`、`O Draw Tubes`、`O Gradient Background`、`O One Texture`、`O Outline`、`O Random Jitter`

## O Extra

### O Draw Shape

把 Grease Pencil 笔画转成实体网格，可膨胀、对称、重网格和平滑。

#### 输入

- `Grease Pencil`：提供要转换成实体形状或管线的 Grease Pencil 笔画。
- `Resolution`：控制生成结果或采样网格的精细度。
- `Inflate`：让形状沿表面法线向外或向内鼓起。
- `Symmetry`：选择要生成或保留的对称方向。
- `Symmetry / Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `Symmetry / Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `Symmetry / Radial`：控制是否围绕中心按径向方式计算。
- `Remesh`：决定是否重建网格拓扑。
- `Remesh / Resolution`：控制生成结果或采样网格的精细度。
- `Remesh / Relax Iterations`：控制松弛计算重复次数；次数越多，分布越均匀。
- `Remesh / Smooth Iterations`：控制平滑重复次数；次数越多，结果越柔和。

#### 输出

- `Mesh`：输出处理后的网格。


### O Draw Tubes

把 Grease Pencil 笔画转成管状网格，可对齐端点、连接、对称及重网格。

#### 输入

- `Grease Pencil`：提供要转换成实体形状或管线的 Grease Pencil 笔画。
- `Resolution`：控制生成结果或采样网格的精细度。
- `Radius Scale`：按比例放大或缩小已有半径。
- `Thickness`：控制实体、描边或管壁的厚度。
- `Fill Caps`：决定开放截面是否封口。
- `Symmetry`：选择要生成或保留的对称方向。
- `Symmetry / Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `Symmetry / Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `Symmetry / Radial`：控制是否围绕中心按径向方式计算。
- `Align Ends`：决定是否整理并对齐开放端点。
- `Align Ends / Align Threshold`：决定相距多近的端点才会被视为需要对齐。
- `Align Ends / Align Iterations`：控制端点对齐要重复计算多少次；次数越多，整理越充分。
- `Remesh`：决定是否重建网格拓扑。
- `Remesh / Connect Distance`：决定相距多近的部分可以连接。
- `Remesh / Resolution`：控制生成结果或采样网格的精细度。
- `Remesh / Relax Iterations`：控制松弛计算重复次数；次数越多，分布越均匀。
- `Remesh / Smooth Iterations`：控制平滑重复次数；次数越多，结果越柔和。

#### 输出

- `Mesh`：输出处理后的网格。


### O Gradient Background

用两种颜色和线性角度生成渐变 World Shader，并保留独立环境光控制。

#### 输入

- `A`：提供第一组参与比较、混合或计算的数据。
- `B`：提供第二组参与比较、混合或计算的数据。
- `Angle`：控制旋转角度或方向角。
- `Invert`：反转当前选择、遮罩或判断结果。
- `Light`：提供光照颜色或光照信息。
- `Strength`：控制效果的整体强弱。
- `Options / Transmission (Cycles)`：控制 Cycles 中光线穿过材质的程度。
- `Options / Location`：指定位置或平移量。
- `Options / Scale`：整体放大或缩小形状、坐标或效果尺度。

#### 输出

- `Shader`：输出可连接到材质或世界表面的着色器。


### O One Texture

从一个 Color 或纹理信号派生粗糙度、凹凸、透明、次表面等通道，生成 Principled BSDF。

#### 妙用

- 只有一张颜色贴图时，快速得到可用的材质起点，再逐项微调表面特征。

#### 输入

- `Color`：提供要使用、混合或处理的颜色。
- `Alpha`：控制整体透明度。
- `Metallic`：控制表面从非金属到金属的程度。
- `IOR`：控制材质折射率，并影响反射与透射的观感。
- `Roughness Min`：设置由输入纹理推导粗糙度时的最低值。
- `Roughness Max`：设置由输入纹理推导粗糙度时的最高值。
- `Bump Distance`：控制由纹理明暗产生的表面凹凸幅度。
- `Coat Weight`：控制「Coat」对最终结果的影响强度。
- `Sheen Weight`：控制「Sheen」对最终结果的影响强度。
- `Emission Strength`：控制材质自身发光的亮度。
- `Alpha / Alpha Min`：设置由输入纹理推导透明度时的最低值。
- `Alpha / Alpha Max`：设置由输入纹理推导透明度时的最高值。
- `Subsurface / Subsurface Weight`：控制「Subsurface」对最终结果的影响强度。
- `Subsurface / Subsurface Scale`：控制次表面散射深入材质内部的距离。
- `Subsurface / Hue`：调整颜色的色相。
- `Subsurface / Saturation`：调整颜色饱和度。
- `Subsurface / Value`：提供要处理、映射或混合的数值。

#### 输出

- `BSDF`：输出可直接连接到材质表面的着色结果。


### O Outline

通过几何外扩和材质设置生成倒壳式轮廓，可加入次级轮廓和松散抖动。

#### 妙用

- 制作漫画轮廓、产品描边，或叠加轻微抖动获得手绘感。

#### 输入

- `Mesh`：提供要处理或作为参考的网格。
- `Thickness`：控制实体、描边或管壁的厚度。
- `Color`：提供要使用、混合或处理的颜色。
- `Light`：提供光照颜色或光照信息。
- `Secondary (Eevee)`：在 Eevee 中启用次级轮廓层。
- `Secondary (Eevee) / Color`：提供要使用、混合或处理的颜色。
- `Secondary (Eevee) / Threshold`：设置判断或筛选生效的分界值。
- `Loose`：决定是否处理没有连接成面的松散点和边。
- `Loose / Weight`：控制每个元素受效果影响的程度。
- `Loose / Frequency`：控制变化出现得有多密集。
- `Loose / Offset`：在原位置、时间或数值基础上增加偏移。
- `Options / Thickness Weight`：控制「Thickness」对最终结果的影响强度。

#### 输出

- `Geometry`：输出处理后的几何。


### O Random Jitter

用随时间步进的噪声位移几何，生成稳定可控的随机抖动动画。

#### 妙用

- 制作定格动画、手绘抖线或机械部件的轻微振动。

#### 输入

- `Geometry`：提供要处理的几何。
- `Strength`：控制每次抖动的位移幅度。
- `Frequency`：控制抖动噪声的空间密度；越高时，相邻位置的变化越细碎。
- `Step Size`：控制随机形态间隔多少帧更新一次；越大时，每个形态停留越久。

#### 输出

- `Geometry`：输出处理后的几何。

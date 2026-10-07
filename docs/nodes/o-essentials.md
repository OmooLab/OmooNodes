# O Essentials 节点参考

本页收录 86 个资产节点，重点说明节点能做什么、参数如何影响结果，以及值得尝试的用法。

机器接口信息由 `node-catalog.json` 单独维护。同名输入属于不同模式时，会用「面板 / 参数」标明它所在的位置。

## 快速索引

- 合成节点：`O Image Info`、`O Relight`、`O Stroke`
- 几何节点：`O Align Edge Ends`、`O Blend`、`O Capsule`、`O Center`、`O Center Line`、`O Connect Adjacent`、`O Curve Deform`、`O Curve Distance Texture`、`O Curve Flow Texture`、`O Curve to Edge`、`O Debug Direction`、`O Debug Direction Field`、`O Debug Edge`、`O Debug Field`、`O Debug Integer`、`O Debug UV`、`O Delete Small Parts`、`O Displace`、`O Edge to Curve`、`O Exploded View`、`O Fast Remesh`、`O Geometry Info`、`O Grid Distribute`、`O Helix`、`O ID Selection`、`O Index Selection`、`O Is Edge Boundary`、`O Is UV Split`、`O Mask by Distance`、`O Mask by Selection`、`O Match Size`、`O Mesh Boolean`、`O Mesh Distance Texture`、`O Mesh Flow Texture`、`O Mix Color`、`O Nearby Selection`、`O Noise Texture`、`O Normalize Attribute`、`O Object to Tangent Space`、`O Pick Instance`、`O Point Deform`、`O Point Grid`、`O Points Distance Texture`、`O Points Flow Texture`、`O Position Selection`、`O Project`、`O Quad Sphere`、`O Random Direction`、`O Random Instance Index`、`O Random Selection`、`O Region Selection`、`O Relax`、`O Resample Edge`、`O Rest Position`、`O Scene Time`、`O Screw`、`O Selection`、`O Set Edge Radius`、`O Shortest Paths`、`O Smooth`、`O Smooth Attributes`、`O Solidfy`、`O Store Selection`、`O Symmetry`、`O Tension`、`O Timing`、`O Torus`、`O Transfer Attributes`、`O Transfer Material`、`O Transfer UV`、`O Transform`、`O Tube`、`O UV Island`、`O UV Tangent`、`O Voxel Remesh`、`O Wireframe`
- 着色器节点：`O Background`、`O Circle`、`O Ensure UV`、`O Grid`、`O Linear`、`O Pixelate`、`O Square`

## 合成节点

### O Image Info

读取合成图像的尺寸关系，输出可用于分辨率无关运算的相对尺寸。

#### 输入

- `Image`：提供要分析或处理的图像。

#### 输出

- `Relative Size`：输出相对于参考分辨率的尺寸比例。


### O Relight

结合图像、法线与遮罩，按给定方向和颜色重新计算方向光，并同时输出光照分量。

#### 妙用

- 在合成阶段补一盏可控方向光，快速调整角色或产品的受光方向。

#### 输入

- `Image`：提供要分析或处理的图像。
- `Normal`：提供表面朝向，用于光照、投射或方向计算。
- `Mask`：限制效果的作用范围；黑白或数值可形成渐变过渡。
- `Direction`：指定效果、投射或形变前进的方向。
- `Color`：提供要使用、混合或处理的颜色。

#### 输出

- `Image`：输出处理后的图像。
- `Light`：输出单独的光照分量。


### O Stroke

综合 Matte、Depth 与 Normal 边缘生成可抖动、可调粗细的合成描边，并叠加到原图。

#### 输入

- `Image`：提供要分析或处理的图像。
- `Matte`：提供前景遮罩或抠像结果。
- `Depth`：提供深度信息或控制沿深度方向的距离。
- `Normal`：提供表面朝向，用于光照、投射或方向计算。
- `General / Thickness`：控制实体、描边或管壁的厚度。
- `General / Color`：提供要使用、混合或处理的颜色。
- `General / Light`：提供光照颜色或光照信息。
- `Loose / Strength`：控制效果的整体强弱。
- `Loose / Frequency`：控制变化出现得有多密集。
- `Loose / Messy`：加入不规则变化，避免端点或排列显得过于整齐。
- `Loose / Offset`：在原位置、时间或数值基础上增加偏移。
- `Options / Exposure`：整体提亮或压暗结果。
- `Options / Gamma`：调整明暗中间调。
- `Options / Blur`：柔化结果，减弱过硬的边界或细节。
- `Options / Matte Weight`：控制「Matte」对最终结果的影响强度。
- `Options / Depth Weight`：控制「Depth」对最终结果的影响强度。
- `Options / Normal Weight`：控制「Normal」对最终结果的影响强度。
- `Options / Normal Threshold`：决定法线方向差异多大时才视为不同区域。

#### 输出

- `Image`：输出处理后的图像。
- `Stroke`：输出单独的描边图像。


## 几何节点

### O Align Edge Ends

迭代拉齐距离阈值内的开放边端点，适合清理后续连接或管线生成前的边。

#### 输入

- `Edge`：提供要处理、筛选或转换的边。
- `Distance Threshold`：决定距离达到什么条件时才产生效果。
- `Iterations`：控制重复计算次数；次数越多通常越充分，也会更慢。

#### 输出

- `Edge`：输出处理或筛选后的边。


### O Blend

在目标几何与 Source 的对应位置之间按 Factor 混合选中元素。

#### 输入

- `Geometry`：提供要处理的几何。
- `Selection`：限制效果作用范围；未选中的部分保持不变。
- `Source`：提供用于采样、匹配、投射或比较的参考几何。
- `Factor`：控制两种状态之间的混合比例或效果强度。

#### 输出

- `Geometry`：输出处理后的几何。


### O Capsule

生成可独立控制顶部和底部封口的胶囊网格，并输出区域选择与 UV。

#### 输入

- `Segments`：控制生成结构沿主要方向的分段精细度。
- `Rings`：控制环形结构沿长度方向的分段数量。
- `Side Segments`：控制侧面沿长度方向的分段精细度。
- `Radius`：控制影响范围、管线粗细或圆形尺寸。
- `Height`：提供位移高度或形状起伏。
- `Options / Top Cap`：决定顶部是否封口。
- `Options / Bottom Cap`：决定底部是否封口。

#### 输出

- `Mesh`：输出处理后的网格。
- `Top`：输出顶部区域选择。
- `Side`：输出侧面区域选择。
- `Bottom`：输出底部区域选择。
- `UV Map`：输出生成或转移后的 UV 坐标。


### O Center

把几何包围盒中心移动到指定 Center。

#### 输入

- `Geometry`：提供要处理的几何。
- `Center`：指定操作围绕的中心位置或目标中心。

#### 输出

- `Geometry`：输出处理后的几何。


### O Center Line

从网格估算并平滑中心线，输出便于进一步曲线处理的边几何。

#### 输入

- `Mesh`：提供要处理或作为参考的网格。
- `Resolution`：控制生成结果或采样网格的精细度。
- `Iterations`：控制重复计算次数；次数越多通常越充分，也会更慢。
- `Ray`：选择沿射线方向进行投射或查找。
- `Options / Smooth Iterations`：控制平滑重复次数；次数越多，结果越柔和。
- `Options / Smooth Weight`：控制每次平滑对原结果的影响强度。

#### 输出

- `Edge`：输出处理或筛选后的边。


### O Connect Adjacent

按 Range 为相邻点建立连接，使用 Selection 限定参与范围。

#### 输入

- `Geometry`：提供要处理的几何。
- `Selection`：限制效果作用范围；未选中的部分保持不变。
- `Range`：控制搜索、选择或影响覆盖的范围。

#### 输出

- `Geometry`：输出处理后的几何。


### O Curve Deform

沿 Curve 弯曲或贴合几何，可控制轴向、偏移、倾斜、权重与中心策略。

#### 妙用

- 让文字、线缆、鳞片或重复结构沿一条曲线弯曲。
- 先制作直线形态，再用曲线统一控制最终走势，方便反复改形。

#### 输入

- `Geometry`：提供要处理的几何。
- `Selection`：限制效果作用范围；未选中的部分保持不变。
- `Curve`：提供控制形状、走势或采样位置的曲线。
- `Offset`：在原位置、时间或数值基础上增加偏移。
- `Tilt`：控制曲线截面沿路径的扭转。
- `Fit to Curve`：让变形长度适配控制曲线，避免只使用曲线的一部分或超出曲线。
- `Orient / Primary Axis`：选择形变或对齐使用的主轴。
- `Orient / Secondary Axis`：选择辅助轴，帮助确定完整朝向。
- `Options / Weight`：控制每个元素受效果影响的程度。
- `Options / Center`：指定操作围绕的中心位置或目标中心。
- `Options / Offset`：在原位置、时间或数值基础上增加偏移。
- `Options / Custom`：启用或提供自定义控制方式。

#### 输出

- `Geometry`：输出处理后的几何。


### O Curve Distance Texture

计算采样位置到曲线或边的距离场，并用 Radius Offset 调整等值面。

#### 输入

- `Curve (Edge)`：提供以网格边表示的曲线。
- `Radius Offset`：在现有半径基础上增加或减少距离。

#### 输出

- `Value`：输出计算后的数值。


### O Curve Flow Texture

从曲线切线、法线或扭转方向生成向量流场，可重采样和平滑。

#### 输入

- `Curve (Edge)`：提供以网格边表示的曲线。
- `Strength`：控制效果的整体强弱。
- `Reverse`：反转方向、顺序或判断结果。
- `Normal/Twist/Tangent`：选择使用法线、扭转或切线来构建方向。
- `Radius`：控制影响范围、管线粗细或圆形尺寸。
- `Options / Resample Length`：控制重采样后相邻点或边的大致间距。
- `Options / Smooth Iterations`：控制平滑重复次数；次数越多，结果越柔和。
- `Options / Smooth`：柔化形状、属性或过渡。

#### 输出

- `Vector`：输出计算后的向量。


### O Curve to Edge

把 Blender Curve 转成仅含边的 Mesh 表示。

#### 输入

- `Curve`：提供控制形状、走势或采样位置的曲线。

#### 输出

- `Edge`：输出处理或筛选后的边。


### O Debug Direction

把几何上的方向向量可视化，并输出规范化后的方向。

#### 输入

- `Geometry`：提供要处理的几何。
- `Direction`：指定效果、投射或形变前进的方向。
- `Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `Normalize`：把结果整理到统一尺度，便于后续混合或比较。
- `Size`：控制整体尺寸或目标包围盒大小。

#### 输出

- `Debug`：输出便于在视口中检查结果的调试几何。
- `Direction`：输出计算后的方向。


### O Debug Direction Field

在平面或体积采样网格上可视化向量场。

#### 输入

- `Container`：提供用于限定内部、外部或计算范围的容器几何。
- `Direction`：指定效果、投射或形变前进的方向。
- `Normalize`：把结果整理到统一尺度，便于后续混合或比较。
- `Type`：选择节点要处理的数据或生成结果类型。
- `Position`：提供要计算或采样的空间位置。
- `Size`：控制整体尺寸或目标包围盒大小。
- `Container / Space`：选择坐标或变换所处的空间。
- `Container / Min`：设置映射、筛选或限制使用的下限。
- `Container / Max`：设置映射、筛选或限制使用的上限。

#### 输出

- `Debug`：输出便于在视口中检查结果的调试几何。


### O Debug Edge

把边转换为可见线框，并把给定属性同步到调试结果。

#### 输入

- `Edge`：提供要处理、筛选或转换的边。
- `Attribute`：提供要读取、处理或写回的属性值。

#### 输出

- `Mesh`：输出处理后的网格。
- `Attribute`：输出处理或采样后的属性。


### O Debug Field

在规则采样网格上把向量或数值场转成可见颜色和调试几何。

#### 输入

- `Container`：提供用于限定内部、外部或计算范围的容器几何。
- `Field`：提供需要采样或可视化的场数据。
- `Normalize`：把结果整理到统一尺度，便于后续混合或比较。
- `Type`：选择节点要处理的数据或生成结果类型。
- `Position`：提供要计算或采样的空间位置。
- `Container / Min`：设置映射、筛选或限制使用的下限。
- `Container / Max`：设置映射、筛选或限制使用的上限。
- `Container / Space`：选择坐标或变换所处的空间。

#### 输出

- `Debug`：输出便于在视口中检查结果的调试几何。
- `Color`：输出计算后的颜色。


### O Debug Integer

把整数或 ID 映射为颜色等可视表示，便于检查分组。

#### 输入

- `Mesh`：提供要处理或作为参考的网格。
- `Integer`：提供要处理或传递的整数属性。
- `Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `Options / Seed`：更换随机结果，同时保持同一数值下结果稳定。

#### 输出

- `Debug`：输出便于在视口中检查结果的调试几何。
- `Color`：输出计算后的颜色。


### O Debug UV

展开或直接显示 UV，并突出 UV Seam、边界及岛屿差异。

#### 妙用

- 在不切换 UV 编辑器的情况下检查断缝、UV 岛和拉伸问题。

#### 输入

- `Mesh`：提供要处理或作为参考的网格。
- `Flat`：决定是否使用平直、无平滑过渡的结果。
- `UV Seam`：提供 UV 接缝选择。
- `Transform / Translation`：指定平移量。
- `Transform / Rotation`：指定旋转量或朝向。
- `Transform / Scale`：整体放大或缩小形状、坐标或效果尺度。
- `Options / UV`：提供纹理坐标，用于采样、转移或空间计算。
- `Options / Seam`：提供接缝选择，用于切分或检查 UV。
- `Options / Seed`：更换随机结果，同时保持同一数值下结果稳定。

#### 输出

- `Debug`：输出便于在视口中检查结果的调试几何。


### O Delete Small Parts

按连通部分大小删除低于 Threshold 的碎片。

#### 输入

- `Mesh`：提供要处理或作为参考的网格。
- `Threshold`：设置判断或筛选生效的分界值。

#### 输出

- `Mesh`：输出处理后的网格。


### O Displace

沿法线、指定方向或向量场移动选中几何，支持 Strength、Height 与 Midlevel。

#### 妙用

- 把 `O Noise Texture` 接到 `Height`，制作水面起伏、地形细节或呼吸式形变。
- 用顶点属性或绘制遮罩限制局部位移，避免整个模型一起变形。

#### 输入

- `Geometry`：提供要处理的几何。
- `Selection`：限制效果作用范围；未选中的部分保持不变。
- `Strength`：统一放大、缩小或反转位移幅度。
- `Direction`：指定顶点移动方向；使用法线模式时通常无需单独连接。
- `Height`：用明暗或数值决定每个位置移动多少，可接纹理、属性或动画信号。
- `Vector`：直接提供每个位置的三维移动量，适合由方向场同时控制方向和距离。
- `Options / Midlevel`：指定高度信号中的静止点；等于此值的位置不移动。

#### 输出

- `Geometry`：输出处理后的几何。


### O Edge to Curve

把仅含边的 Mesh 转成 Curve。

#### 输入

- `Edge`：提供要处理、筛选或转换的边。

#### 输出

- `Curve`：输出处理后的曲线。


### O Exploded View

按连通块或 Group ID 从整体中心向外缩放各部分，形成爆炸视图。 概念命名可参照 [Houdini 同名或近似节点](https://www.sidefx.com/docs/houdini/nodes/sop/explodedview.html)。

#### 妙用

- 制作产品拆解图、装配动画，或快速检查互相遮挡的零件。

#### 输入

- `Geometry`：提供要处理的几何。
- `Scale`：整体放大或缩小形状、坐标或效果尺度。
- `Group ID`：用编号把元素分组，让每组独立计算。

#### 输出

- `Geometry`：输出处理后的几何。


### O Fast Remesh

以较少步骤重建较均匀拓扑，并可松弛、平滑着色及尝试修复 UV。

#### 输入

- `Mesh`：提供要处理或作为参考的网格。
- `Resolution`：控制生成结果或采样网格的精细度。
- `Relax Iterations`：控制松弛计算重复次数；次数越多，分布越均匀。
- `Options / Shade Smooth`：决定结果是否使用平滑着色。
- `Options / Relax Weight`：控制松弛对当前位置的影响强度。
- `Options / Fix Topo Steps`：控制拓扑修复过程尝试多少步。
- `Options / Fix UV`：在拓扑变化后尝试修复和保留原有 UV。
- `Options / Fix UV Range`：限制「Fix UV」相关处理的作用范围。
- `Options / UV`：提供纹理坐标，用于采样、转移或空间计算。

#### 输出

- `Mesh`：输出处理后的网格。


### O Geometry Info

输出几何的包围盒尺寸、中心点与顶点中位位置。

#### 输入

- `Geometry`：提供要处理的几何。

#### 输出

- `Size`：输出几何包围盒尺寸。
- `Center Point`：输出包围盒中心位置。
- `Median Point`：输出顶点位置的中位点。


### O Grid Distribute

在网格表面按间距分布点，支持随机筛选、半径约束和松弛。

#### 妙用

- 在曲面上生成规则但不过分机械的散布点，用于植被、铆钉或面板细节。

#### 输入

- `Mesh`：提供要处理或作为参考的网格。
- `Spacing`：控制相邻点或实例之间的目标间距。
- `Radius`：控制影响范围、管线粗细或圆形尺寸。
- `Random`：加入随机变化，打破过于规则的结果。
- `Options / Random Selection`：限制哪些随机选中的元素参与处理。
- `Options / Relax Iterations`：控制松弛计算重复次数；次数越多，分布越均匀。
- `Options / Seed`：更换随机结果，同时保持同一数值下结果稳定。

#### 输出

- `Points`：输出生成或处理后的点。


### O Helix

按角度、半径和高度生成螺旋边。

#### 输入

- `Segments`：控制生成结构沿主要方向的分段精细度。
- `Angle`：控制旋转角度或方向角。
- `Radius`：控制影响范围、管线粗细或圆形尺寸。
- `Height`：提供位移高度或形状起伏。

#### 输出

- `Edge`：输出处理或筛选后的边。


### O ID Selection

按 ID 字段选择元素，并支持反选。

#### 输入

- `ID`：提供稳定编号，用于选择、分组或可重复随机。
- `Invert`：反转当前选择、遮罩或判断结果。

#### 输出

- `Selection`：输出满足条件的元素选择。


### O Index Selection

按 Index 字段选择元素，并支持反选。

#### 输入

- `Index`：按元素序号控制选择或计算。
- `Invert`：反转当前选择、遮罩或判断结果。

#### 输出

- `Selection`：输出满足条件的元素选择。


### O Is Edge Boundary

判断当前边是否位于网格边界。

#### 输出

- `Is Edge Boundary`：标记处于网格边界的边。


### O Is UV Split

判断边两侧 UV 是否断开，并区分同岛与异岛。

#### 输入

- `UV`：提供纹理坐标，用于采样、转移或空间计算。

#### 输出

- `Is UV Split`：标记 UV 在边两侧断开的位置。
- `Same Island`：标记边两侧属于同一 UV 岛的位置。
- `Different Island`：标记边两侧属于不同 UV 岛的位置。


### O Mask by Distance

计算到 Source 的距离，输出距离、遮罩以及被遮罩的几何。

#### 输入

- `Geometry`：提供要处理的几何。
- `Source`：提供用于采样、匹配、投射或比较的参考几何。
- `Max Distance`：限制搜索、投射或影响能够到达的最远距离。

#### 输出

- `Geometry`：输出处理后的几何。
- `Mask`：输出可继续用于限制其他效果的遮罩。
- `Distance`：输出到参考目标的距离。


### O Mask by Selection

把一个 Selection 扩展成基于距离或拓扑的平滑遮罩。

#### 输入

- `Geometry`：提供要处理的几何。
- `Selection`：限制效果作用范围；未选中的部分保持不变。
- `Method`：选择节点采用的计算方法。
- `Max Distance`：限制搜索、投射或影响能够到达的最远距离。
- `Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `Solid`：决定结果是否保持或生成封闭实体。
- `Smooth`：柔化形状、属性或过渡。
- `Smooth Iterations`：控制平滑重复次数；次数越多，结果越柔和。

#### 输出

- `Geometry`：输出处理后的几何。
- `Mask`：输出可继续用于限制其他效果的遮罩。


### O Match Size

按目标 Size 缩放几何并把中心对齐到指定 Center。 概念命名可参照 [Houdini 同名或近似节点](https://www.sidefx.com/docs/houdini/nodes/sop/matchsize.html)。

#### 输入

- `Geometry`：提供要处理的几何。
- `Size`：控制整体尺寸或目标包围盒大小。
- `Center`：指定操作围绕的中心位置或目标中心。

#### 输出

- `Geometry`：输出处理后的几何。


### O Mesh Boolean

提供 Union、Intersect、Difference 等布尔模式，并带属性平滑、体素预览和交线输出。

#### 妙用

- 制作可随输入模型更新的门窗开洞、拼接结构和交叠线。

#### 输入

- `A`：提供第一组参与比较、混合或计算的数据。
- `B`：提供第二组参与比较、混合或计算的数据。
- `Mode`：选择节点采用的工作方式。
- `Method`：选择节点采用的计算方法。
- `Surface Attribute / Float`：提供要处理或传递的小数属性。
- `Surface Attribute / Integer`：提供要处理或传递的整数属性。
- `Surface Attribute / Vector`：提供要处理、转换或可视化的向量。
- `Surface Attribute / Color`：提供要使用、混合或处理的颜色。
- `Smooth Intersecting`：柔化布尔运算产生的相交边，减弱生硬折线。
- `Smooth Intersecting / Max Distance`：限制搜索、投射或影响能够到达的最远距离。
- `Smooth Intersecting / Iterations`：控制重复计算次数；次数越多通常越充分，也会更慢。
- `Preview`：启用便于观察过程的预览结果。
- `Preview / Resolution`：控制生成结果或采样网格的精细度。
- `Preview / Iterations`：控制重复计算次数；次数越多通常越充分，也会更慢。

#### 输出

- `Mesh`：输出处理后的网格。
- `Intersecting Edges`：标记布尔运算产生的相交边。


### O Mesh Distance Texture

输出采样位置到网格表面的有符号或无符号距离。

#### 输入

- `Mesh`：提供要处理或作为参考的网格。
- `Unsigned`：只保留距离大小，不区分表面内外。
- `Offset`：在原位置、时间或数值基础上增加偏移。

#### 输出

- `Value`：输出计算后的数值。


### O Mesh Flow Texture

从网格表面方向生成向量流场，可控制强度、反向与作用半径。

#### 输入

- `Mesh`：提供要处理或作为参考的网格。
- `Strength`：控制效果的整体强弱。
- `Reverse`：反转方向、顺序或判断结果。
- `Radius`：控制影响范围、管线粗细或圆形尺寸。

#### 输出

- `Vector`：输出计算后的向量。


### O Mix Color

按 Factor 混合两种颜色。

#### 输入

- `Factor`：控制两种状态之间的混合比例或效果强度。
- `A`：提供第一组参与比较、混合或计算的数据。
- `B`：提供第二组参与比较、混合或计算的数据。

#### 输出

- `Color`：输出计算后的颜色。


### O Nearby Selection

选择 Point Index 周围 Range 内的点，可排除自身或反选。

#### 输入

- `Point Index`：指定作为中心或参考的点序号。
- `Range`：控制搜索、选择或影响覆盖的范围。
- `Exclude Self`：排除元素自身，避免把自己算作邻近目标。
- `Invert`：反转当前选择、遮罩或判断结果。

#### 输出

- `Selection`：输出满足条件的元素选择。


### O Noise Texture

生成可重映射范围和中点的噪声数值与向量，供位移或场运算使用。

#### 妙用

- 驱动位移、颜色、粗糙度或随机选择，让变化保持可重复且易于调节。

#### 输入

- `Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `Strength`：控制效果的整体强弱。
- `Midlevel`：指定高度信号中代表「不发生位移」的基准值。
- `Min`：设置映射、筛选或限制使用的下限。
- `Max`：设置映射、筛选或限制使用的上限。
- `Options / W`：推动噪声随时间连续变化，适合制作不会跳帧的动态起伏。
- `Options / Scale`：控制噪声纹理的空间尺寸；数值越大，纹理变化越密。
- `Options / Detail`：增加更小尺度的噪声层次；提高后会更丰富，也更碎。
- `Options / Roughness`：控制不同尺度噪声混合后的粗糙程度。
- `Options / Lacunarity`：控制噪声不同尺度之间的频率增长速度。
- `Options / Distortion`：控制形状或纹理被扰动的程度。
- `Options / Sample Position`：指定噪声在空间中的采样位置；移动它可以让纹理流动。

#### 输出

- `Vector`：输出三方向噪声，可直接用作方向或位置扰动。
- `Value`：输出经过范围与中点整理的噪声数值，可直接驱动位移或遮罩。


### O Normalize Attribute

在选中域上把浮点 Attribute 归一化，输出标准化结果。

#### 输入

- `Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `Geometry`：提供要处理的几何。
- `Selection`：限制效果作用范围；未选中的部分保持不变。
- `Attribute`：提供要读取、处理或写回的属性值。

#### 输出

- `Result`：输出节点最终计算结果。


### O Object to Tangent Space

结合 UV Tangent 与 Normal，把对象空间方向转换到切线空间。

#### 输入

- `UV Tangent`：提供沿 UV 方向计算得到的表面切线。
- `Normal`：提供表面朝向，用于光照、投射或方向计算。

#### 输出

- `Normal`：输出计算或处理后的表面法线。


### O Pick Instance

按当前求值元素的 Index 从输入实例集合中挑选单个实例。

#### 输入

- `Geometry`：提供要处理的几何。

#### 输出

- `Instance`：输出选中的实例。


### O Point Deform

根据 Source 点相对 Rest Position 的变化，把捕获到的变形传递给目标几何。 概念命名可参照 [Houdini 同名或近似节点](https://www.sidefx.com/docs/houdini/nodes/sop/pointdeform.html)。

#### 妙用

- 用低模代理体驱动高模、毛发或附着细节，降低复杂形变的编辑成本。

#### 输入

- `Geometry`：提供要处理的几何。
- `Selection`：限制效果作用范围；未选中的部分保持不变。
- `Source`：提供用于采样、匹配、投射或比较的参考几何。
- `Rest Positon`：提供未变形时的位置，作为形变比较基准。
- `Options / Weight`：控制每个元素受效果影响的程度。
- `Options / Smooth Iterations`：控制平滑重复次数；次数越多，结果越柔和。
- `Options / Smooth Weight`：控制每次平滑对原结果的影响强度。

#### 输出

- `Geometry`：输出处理后的几何。


### O Point Grid

在选定平面或体积范围内生成规则点阵，可限制内外区域。

#### 输入

- `Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `Space`：选择坐标或变换所处的空间。
- `Radius`：控制影响范围、管线粗细或圆形尺寸。
- `Min`：设置映射、筛选或限制使用的下限。
- `Max`：设置映射、筛选或限制使用的上限。
- `Position`：提供要计算或采样的空间位置。
- `Inside`：决定使用区域内部还是外部。

#### 输出

- `Points`：输出生成或处理后的点。


### O Points Distance Texture

输出采样位置到点集的距离场，并支持半径偏移。

#### 输入

- `Points`：提供用于采样、变形或生成场的点。
- `Radius Offset`：在现有半径基础上增加或减少距离。

#### 输出

- `Value`：输出计算后的数值。


### O Points Flow Texture

根据点集生成向量流场，可控制方向、强度和作用半径。

#### 输入

- `Points`：提供用于采样、变形或生成场的点。
- `Strength`：控制效果的整体强弱。
- `Reverse`：反转方向、顺序或判断结果。
- `Radius`：控制影响范围、管线粗细或圆形尺寸。

#### 输出

- `Vector`：输出计算后的向量。


### O Position Selection

按坐标轴、比较方式与 A/B 阈值选择位置范围。

#### 输入

- `Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `Vector`：提供要处理、转换或可视化的向量。
- `Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `N`：指定触发或采样使用的第几个时间步。
- `A`：提供第一组参与比较、混合或计算的数据。
- `B`：提供第二组参与比较、混合或计算的数据。
- `Invert`：反转当前选择、遮罩或判断结果。

#### 输出

- `Selection`：输出满足条件的元素选择。


### O Project

按最近距离或正负方向射线把选中几何投射到 Source，并支持自定义方向和权重。

#### 妙用

- 把道路、贴花、线条或散布点贴到起伏表面。

#### 输入

- `Geometry`：提供要处理的几何。
- `Selection`：限制效果作用范围；未选中的部分保持不变。
- `Source`：提供用于采样、匹配、投射或比较的参考几何。
- `Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `Positive Weight`：控制「Positive」对最终结果的影响强度。
- `Negative Weight`：控制「Negative」对最终结果的影响强度。
- `Max Distance`：限制搜索、投射或影响能够到达的最远距离。
- `Options / Weight`：控制每个元素受效果影响的程度。
- `Options / Radius Offset`：在现有半径基础上增加或减少距离。
- `Options / Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `Options / Custom`：启用或提供自定义控制方式。
- `Options / Normal Smooth`：柔化用于计算的法线，减少方向场中的突变。

#### 输出

- `Geometry`：输出处理后的几何。


### O Quad Sphere

生成以四边面为主的球体并输出 UV。

#### 输入

- `Segments`：控制生成结构沿主要方向的分段精细度。
- `Radius`：控制影响范围、管线粗细或圆形尺寸。

#### 输出

- `Mesh`：输出处理后的网格。
- `UV Map`：输出生成或转移后的 UV 坐标。


### O Random Direction

在给定 Direction 周围生成随机方向与旋转，支持径向和轴向扩散。

#### 输入

- `Direction`：指定效果、投射或形变前进的方向。
- `Spread`：控制随机方向或分布向外扩散的程度。
- `Axial Spread`：控制随机方向沿主轴扩散的程度。
- `ID`：提供稳定编号，用于选择、分组或可重复随机。
- `Seed`：更换随机结果，同时保持同一数值下结果稳定。

#### 输出

- `Direction`：输出计算后的方向。
- `Rotation`：输出计算后的旋转。


### O Random Instance Index

按 A–E 权重随机生成 Instance Index。

#### 输入

- `A`：提供第一组参与比较、混合或计算的数据。
- `B`：提供第二组参与比较、混合或计算的数据。
- `C`：提供当前模式下的第三组数据或权重。
- `D`：提供当前模式下的第四组数据或权重。
- `E`：提供当前模式下的第五组数据或权重。
- `Options / Seed`：更换随机结果，同时保持同一数值下结果稳定。

#### 输出

- `Instance Index`：输出要从实例集合中选择的序号。


### O Random Selection

按 Factor、ID 与 Seed 生成稳定的随机选择。

#### 输入

- `Factor`：控制两种状态之间的混合比例或效果强度。
- `ID`：提供稳定编号，用于选择、分组或可重复随机。
- `Seed`：更换随机结果，同时保持同一数值下结果稳定。

#### 输出

- `Selection`：输出满足条件的元素选择。


### O Region Selection

判断元素是否位于 Region Mesh 内，并支持反选。

#### 输入

- `Region Mesh`：提供用于判断内外区域的网格。
- `Invert`：反转当前选择、遮罩或判断结果。

#### 输出

- `Selection`：输出满足条件的元素选择。


### O Relax

迭代平滑点分布，可固定边界、投射回 Source 并按网格岛限制。 概念命名可参照 [Houdini 同名或近似节点](https://www.sidefx.com/docs/houdini/nodes/sop/relax.html)。

#### 输入

- `Geometry`：提供要处理的几何。
- `Selection`：限制效果作用范围；未选中的部分保持不变。
- `Iterations`：控制重复计算次数；次数越多通常越充分，也会更慢。
- `Options / Weight`：控制每个元素受效果影响的程度。
- `Options / Positive Weight`：控制「Positive」对最终结果的影响强度。
- `Options / Negative Weight`：控制「Negative」对最终结果的影响强度。
- `Options / Max Distance`：限制搜索、投射或影响能够到达的最远距离。
- `Options / Source`：提供用于采样、匹配、投射或比较的参考几何。
- `Options / Source`：提供用于采样、匹配、投射或比较的参考几何。
- `Options / Mesh Island`：按互不连接的网格块分别处理。
- `Options / Source Mesh Island`：按参考网格的独立块分组采样，避免跨块传递。

#### 输出

- `Geometry`：输出处理后的几何。


### O Resample Edge

把边转换为曲线后按 Length 重采样，再转回边并合并近点。

#### 输入

- `Edge`：提供要处理、筛选或转换的边。
- `Selection`：限制效果作用范围；未选中的部分保持不变。
- `Length`：控制生成、重采样或搜索使用的长度。
- `Options / Merge Distance`：决定相距多近的点会被合并。

#### 输出

- `Edge`：输出处理或筛选后的边。


### O Rest Position

保存并输出几何的 Rest Position，供后续变形与张力计算使用。

#### 输入

- `Geometry`：提供要处理的几何。

#### 输出

- `Geometry`：输出处理后的几何。
- `Rest Positon`：输出记录下来的未变形位置。


### O Scene Time

把场景时间按 Step 量化，输出步进秒数。

#### 输入

- `Step`：控制时间或计算按多大步长前进。

#### 输出

- `Step Seconds`：输出按步长量化后的时间。


### O Screw

围绕指定中心轴旋转并推进输入网格，生成旋转体或螺纹结构。

#### 输入

- `Mesh`：提供要处理或作为参考的网格。
- `Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `Angle`：控制旋转角度或方向角。
- `Screw`：控制绕轴旋转同时前进的螺旋量。
- `Iterations`：控制重复计算次数；次数越多通常越充分，也会更慢。
- `Steps`：控制过程被拆分成多少步。
- `Options / Center`：指定操作围绕的中心位置或目标中心。
- `Options / Axis`：选择计算、变换或生成结构所沿的轴。

#### 输出

- `Mesh`：输出处理后的网格。


### O Selection

读取指定名称的布尔选择属性，并支持反选。

#### 输入

- `Name`：指定要读取或写入的属性名称。
- `Invert`：反转当前选择、遮罩或判断结果。

#### 输出

- `Selection`：输出满足条件的元素选择。


### O Set Edge Radius

在选中边上存储或设置后续管线节点使用的半径。

#### 输入

- `Edge`：提供要处理、筛选或转换的边。
- `Selection`：限制效果作用范围；未选中的部分保持不变。
- `Radius`：控制影响范围、管线粗细或圆形尺寸。

#### 输出

- `Edge`：输出处理或筛选后的边。


### O Shortest Paths

从 Root 计算加权最短路径，输出路径边、总成本与路径因子。

#### 输入

- `Edge`：提供要处理、筛选或转换的边。
- `Selection`：限制效果作用范围；未选中的部分保持不变。
- `Root`：指定最短路径开始计算的根元素。
- `Cost`：为路径计算提供每一步的代价或权重。
- `Merged`：决定是否把生成结果中彼此重合或接近的部分合并。

#### 输出

- `Edge`：输出处理或筛选后的边。
- `Total Cost`：输出从根元素到当前位置的累计路径代价。
- `Factor`：输出可用于后续混合或控制强度的系数。


### O Smooth

迭代平滑选中几何，可通过 Pin Sharp 和 Pin Boundary 保留特征。

#### 输入

- `Geometry`：提供要处理的几何。
- `Selection`：限制效果作用范围；未选中的部分保持不变。
- `Iterations`：控制重复计算次数；次数越多通常越充分，也会更慢。
- `Pin Sharp`：尽量固定尖锐特征，避免被平滑掉。
- `Pin Boundary`：固定边界，避免平滑或松弛时轮廓收缩。
- `Options / Weight`：控制每个元素受效果影响的程度。

#### 输出

- `Geometry`：输出处理后的几何。


### O Smooth Attributes

在指定域上迭代平滑 Float、Vector 或 Color 属性。

#### 输入

- `Mesh`：提供要处理或作为参考的网格。
- `Selection`：限制效果作用范围；未选中的部分保持不变。
- `Float`：提供要处理或传递的小数属性。
- `Vector`：提供要处理、转换或可视化的向量。
- `Color`：提供要使用、混合或处理的颜色。
- `on`：打开或关闭这一项处理。
- `Iterations`：控制重复计算次数；次数越多通常越充分，也会更慢。
- `Weight`：控制每个元素受效果影响的程度。

#### 输出

- `Mesh`：输出处理后的网格。


### O Solidfy

为网格增加厚度，并输出侧面选择。

#### 输入

- `Mesh`：提供要处理或作为参考的网格。
- `Thickness`：控制实体、描边或管壁的厚度。
- `Offset`：在原位置、时间或数值基础上增加偏移。

#### 输出

- `Geometry`：输出处理后的几何。
- `Side`：输出侧面区域选择。


### O Store Selection

把当前 Selection 以给定 Name 存入指定几何域。

#### 输入

- `Geometry`：提供要处理的几何。
- `Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `Selection`：限制效果作用范围；未选中的部分保持不变。
- `Name`：指定要读取或写入的属性名称。

#### 输出

- `Geometry`：输出处理后的几何。


### O Symmetry

按轴镜像或径向复制几何，生成对称结构。

#### 输入

- `Geometry`：提供要处理的几何。
- `Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `Radial`：控制是否围绕中心按径向方式计算。

#### 输出

- `Geometry`：输出处理后的几何。


### O Tension

比较当前位置与 Rest Position，输出形变张力场。

#### 输入

- `Rest Position`：提供未变形时的位置，作为形变比较基准。

#### 输出

- `O Tension`：输出形变产生的张力值。


### O Timing

在指定第 N 帧条件下输出布尔时序信号。

#### 输入

- `Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `N`：指定触发或采样使用的第几个时间步。

#### 输出

- `Boolean`：输出布尔判断结果。


### O Torus

生成可控主半径、次半径和分段数的圆环网格及 UV。

#### 输入

- `Major Segments`：控制主体一圈的分段精细度。
- `Minor Segments`：控制截面一圈的分段精细度。
- `Major Radius`：控制圆环或螺旋主体的半径。
- `Minor Radius`：控制圆环截面或次级结构的半径。

#### 输出

- `Mesh`：输出处理后的网格。
- `UV Map`：输出生成或转移后的 UV 坐标。


### O Transfer Attributes

从 Source 采样并写入 Float、Integer、Vector 或 Color 属性，支持跨域和分组。 概念命名可参照 [Houdini 同名或近似节点](https://www.sidefx.com/docs/houdini/nodes/sop/attribtransfer.html)。

#### 妙用

- 重拓扑或重网格后，把颜色、遮罩、方向等数据从原模型传回新模型。

#### 输入

- `Mesh`：提供要处理或作为参考的网格。
- `Selection`：限制效果作用范围；未选中的部分保持不变。
- `Source`：提供用于采样、匹配、投射或比较的参考几何。
- `Float`：提供要处理或传递的小数属性。
- `Integer`：提供要处理或传递的整数属性。
- `Vector`：提供要处理、转换或可视化的向量。
- `Color`：提供要使用、混合或处理的颜色。
- `on`：打开或关闭这一项处理。
- `Evaluate on`：选择在哪一类几何元素上计算结果。
- `Options / Group ID`：用编号把元素分组，让每组独立计算。
- `Options / Sample Position`：指定去参考几何上查询数据的位置。
- `Options / Sample Group ID`：限定从相同分组中采样，避免数据串到其他组。

#### 输出

- `Mesh`：输出处理后的网格。


### O Transfer Material

按采样位置或 UV Island 从 Source 转移材质分配。

#### 输入

- `Mesh`：提供要处理或作为参考的网格。
- `Source`：提供用于采样、匹配、投射或比较的参考几何。
- `Options / UV Island`：按 UV 岛分组或限制处理范围。
- `Options / UV Island`：按 UV 岛分组或限制处理范围。
- `Options / UV`：提供纹理坐标，用于采样、转移或空间计算。

#### 输出

- `Mesh`：输出处理后的网格。


### O Transfer UV

从 Source 向目标网格转移 UV，并可按 UV Island 和 Fix 范围修正断裂。

#### 输入

- `Mesh`：提供要处理或作为参考的网格。
- `Source`：提供用于采样、匹配、投射或比较的参考几何。
- `Menu`：选择节点的工作模式；切换后相关输入也会随之变化。
- `Fix`：选择需要固定、不参与调整的部分。
- `Options / UV Island`：按 UV 岛分组或限制处理范围。
- `Options / UV Island`：按 UV 岛分组或限制处理范围。
- `Options / Fix Range`：限制「Fix」相关处理的作用范围。
- `Options / UV`：提供纹理坐标，用于采样、转移或空间计算。

#### 输出

- `Mesh`：输出处理后的网格。


### O Transform

对选中几何或组件应用平移、旋转、缩放或矩阵，并支持软选择。

#### 输入

- `Geometry`：提供要处理的几何。
- `Selection`：限制效果作用范围；未选中的部分保持不变。
- `Mode`：选择节点采用的工作方式。
- `Translation`：指定平移量。
- `Rotation`：指定旋转量或朝向。
- `Scale`：整体放大或缩小形状、坐标或效果尺度。
- `Transform`：提供完整的平移、旋转和缩放变换。
- `Soft`：让硬选择变成带渐变的柔和影响。
- `Options / Soft Iterations`：控制柔和范围向外扩展和过渡的次数。

#### 输出

- `Geometry`：输出处理后的几何。


### O Tube

把边转换为可调分辨率、半径和厚度的管状网格，可封口和连接近端点。

#### 输入

- `Edge`：提供要处理、筛选或转换的边。
- `Resolution`：控制生成结果或采样网格的精细度。
- `Radius Scale`：按比例放大或缩小已有半径。
- `Thickness`：控制实体、描边或管壁的厚度。
- `Shade Smooth`：决定结果是否使用平滑着色。
- `Fill Caps`：决定开放截面是否封口。
- `Connect`：决定是否连接彼此接近或相邻的部分。
- `Connect / Distance Threshold`：决定距离达到什么条件时才产生效果。
- `Connect / Color`：提供要使用、混合或处理的颜色。

#### 输出

- `Mesh`：输出处理后的网格。


### O UV Island

根据 UV Split 生成稳定的 UV Island 标识。

#### 输入

- `UV`：提供纹理坐标，用于采样、转移或空间计算。

#### 输出

- `UV Island`：输出稳定的 UV 岛编号。


### O UV Tangent

从网格 UV 计算并存储 UV Tangent。

#### 输入

- `Mesh`：提供要处理或作为参考的网格。
- `Options / UV`：提供纹理坐标，用于采样、转移或空间计算。

#### 输出

- `Mesh`：输出处理后的网格。
- `UV Tangent`：输出沿 UV 方向的表面切线。


### O Voxel Remesh

体素化并重建网格，可控制分辨率、适应性、拓扑旋转与后续松弛。 概念命名可参照 [Houdini 同名或近似节点](https://www.sidefx.com/docs/houdini/nodes/sop/remesh.html)。

#### 妙用

- 把扫描、布尔碎片或相交网格先统一成连续表面，再继续平滑和变形。

#### 输入

- `Mesh`：提供要处理或作为参考的网格。
- `Resolution`：控制生成结果或采样网格的精细度。
- `Relax Iterations`：控制松弛计算重复次数；次数越多，分布越均匀。
- `Options / Shade Smooth`：决定结果是否使用平滑着色。
- `Options / Relax Weight`：控制松弛对当前位置的影响强度。
- `Options / Threshold`：设置判断或筛选生效的分界值。
- `Options / Adaptivity`：减少平坦区域的面数，同时尽量保留轮廓和细节。
- `Options / Topo Rotation`：沿网格拓扑调整方向，使重建后的边流转向。

#### 输出

- `Mesh`：输出处理后的网格。


### O Wireframe

把选中网格边转换成具有 Radius 和 Resolution 的线框几何。

#### 输入

- `Mesh`：提供要处理或作为参考的网格。
- `Selection`：限制效果作用范围；未选中的部分保持不变。
- `Resolution`：控制生成结果或采样网格的精细度。
- `Radius`：控制影响范围、管线粗细或圆形尺寸。

#### 输出

- `Mesh`：输出处理后的网格。


## 着色器节点

### O Background

构建可分别控制可见背景、环境光和 Cycles 透射行为的 World Shader。

#### 输入

- `Color`：提供要使用、混合或处理的颜色。
- `Strength`：控制效果的整体强弱。
- `Light`：提供光照颜色或光照信息。
- `Strength`：控制效果的整体强弱。
- `Options / Transmission (Cycles)`：控制 Cycles 中光线穿过材质的程度。

#### 输出

- `Shader`：输出可连接到材质或世界表面的着色器。


### O Circle

生成二维圆形遮罩 Fac 与径向 Gradient。

#### 输入

- `Radius`：控制影响范围、管线粗细或圆形尺寸。
- `Vector`：提供要处理、转换或可视化的向量。

#### 输出

- `Fac`：输出可作为遮罩或混合系数使用的数值。
- `Gradient`：输出形状边缘或方向上的渐变值。


### O Ensure UV

规范输入纹理坐标，确保下游二维纹理获得稳定 UV。

#### 输入

- `Vector`：提供要处理、转换或可视化的向量。

#### 输出

- `Vector`：输出计算后的向量。


### O Grid

把坐标量化或重复为 X×Y 网格坐标。

#### 输入

- `X`：控制 X 方向的尺寸、分段或数值。
- `Y`：控制 Y 方向的尺寸、分段或数值。
- `Vector`：提供要处理、转换或可视化的向量。

#### 输出

- `Vector`：输出计算后的向量。


### O Linear

按 Angle 生成线性 Fac 与 Gradient。

#### 输入

- `Angle`：控制旋转角度或方向角。
- `Vector`：提供要处理、转换或可视化的向量。

#### 输出

- `Fac`：输出可作为遮罩或混合系数使用的数值。
- `Gradient`：输出形状边缘或方向上的渐变值。


### O Pixelate

按 X×Y 分辨率量化二维坐标，形成像素化采样。

#### 输入

- `X`：控制 X 方向的尺寸、分段或数值。
- `Y`：控制 Y 方向的尺寸、分段或数值。
- `Vector`：提供要处理、转换或可视化的向量。

#### 输出

- `Vector`：输出计算后的向量。


### O Square

生成可调 X/Y 尺寸的矩形遮罩 Fac 与边缘 Gradient。

#### 输入

- `X`：控制 X 方向的尺寸、分段或数值。
- `Y`：控制 Y 方向的尺寸、分段或数值。
- `Vector`：提供要处理、转换或可视化的向量。

#### 输出

- `Fac`：输出可作为遮罩或混合系数使用的数值。
- `Gradient`：输出形状边缘或方向上的渐变值。

# Mindmap Layout Algorithms

## Non-layered Tidy Trees (2014)

Thuật toán của A.J. van der Ploeg trong paper "Drawing Non-layered Tidy Trees in Linear Time" (Software: Practice and Experience, 2014). Khác với Reingold-Tilford truyền thống yêu cầu nodes cùng depth phải align theo layers, thuật toán này cho phép nodes có height khác nhau, tạo layout compact hơn đáng kể.

Thuật toán là modification của Reingold-Tilford với O(n) runtime. Proof of correctness phức tạp hơn vì invariant của bản gốc không còn đúng với non-layered case. Paper cũng fix bug trong Walker's algorithm extensions.

Implementations hiện đại (như zxch3n/tidy) mở rộng thêm partial re-layout O(d) khi edit nodes, trong đó d là depth của node thay đổi. Nếu re-layout > 16ms sẽ gây lag - quan trọng cho mindmap editors.

## Readable Tree Layouts (2023)

Paper mới nhất từ IEEE TVCG bởi Kobourov et al. giải quyết vấn đề scalability với trees hàng trăm nghìn nodes. Đảm bảo: no edge crossings, no label overlaps, preserve edge lengths, compact output.

Phương pháp: (1) khởi tạo crossing-free layout, (2) force-directed improvement loại bỏ label overlaps, (3) fine-tuning resize. Implementation: BatchTree trên GitHub.

## Aesthetic Layouts

**Balloon Tree** - Cải tiến radial với children xếp trong "balloon" sectors. Compact hơn radial thông thường, parameters: ParentChildSpacing, ChildWedge, RootWedge.

**Organic/Curved Branches (Ayoa)** - Branches cong tự nhiên như vẽ tay, không dùng thuật toán cố định mà cho user control points để điều chỉnh curves. Kích thích tư duy sáng tạo.

**Sunburst** - Root là circle ở center, children là ring segments. Đẹp cho hierarchies với size encoding, nhưng user performance kém hơn icicle theo studies.

## Classic Algorithms

**Reingold-Tilford (1981)** - Thuật toán nền tảng: nodes cùng depth align, parent centered, subtrees mirror-symmetric.

**Buchheim (2002)** - Fix Walker từ O(n²) → O(n), được D3.js sử dụng.

**Force-Directed** - Mô phỏng vật lý Coulomb + Hooke's law. Tạo layout organic, symmetric tự nhiên.

## Resources

### Papers
- [Readable Tree Layouts - IEEE TVCG (2023)](https://ieeexplore.ieee.org/document/10122175)
- [Van der Ploeg - Non-layered Tidy Trees (2014)](https://onlinelibrary.wiley.com/doi/abs/10.1002/spe.2213)
- [Buchheim et al. - Improving Walker's Algorithm (2002)](https://link.springer.com/chapter/10.1007/3-540-36151-0_32)
- [Reingold-Tilford Original Paper (1981)](https://reingold.co/tidier-drawings.pdf)
- [Force-Directed Drawing Algorithms](https://cs.brown.edu/people/rtamassi/gdhandbook/chapters/force-directed.pdf)

### JavaScript
- [BatchTree - Readable layouts (2023)](https://github.com/khaled-rahman/BatchTree)
- [zxch3n/tidy - Partial re-layout O(d)](https://github.com/zxch3n/tidy)
- [d3-flextree - Variable node sizes](https://github.com/Klortho/d3-flextree)
- [non-layered-tidy-tree-layout](https://github.com/stetrevor/non-layered-tidy-tree-layout)
- [entitree-flex - Van der Ploeg](https://github.com/codeledge/entitree-flex)
- [mindmap-layouts npm](https://github.com/leungwensen/mindmap-layouts)
- [@plait/layouts - Mindmap](https://www.npmjs.com/package/@plait/layouts)
- [D3-Force](https://github.com/d3/d3-force)
- [D3 Sunburst](https://observablehq.com/@d3/sunburst)

### Python
- [py_treedraw - Walker algorithm](https://github.com/cvzi/py_treedraw)
- [layoutTree - Buchheim algorithm](https://github.com/is55555/layoutTree)

### Java
- [non-layered-tidy-trees - Original Van der Ploeg](https://github.com/cwi-swat/non-layered-tidy-trees)
- [timelytree - Buchheim-Walker](https://github.com/cwi-swat/timelytree)

### PHP
- [ReingoldTilford](https://github.com/stefan-loewe/ReingoldTilford)

### Articles
- [Algorithm for Drawing Trees - Rachel Lim](https://rachel53461.wordpress.com/2014/04/20/algorithm-for-drawing-trees/)
- [Drawing Presentable Trees - Bill Mill](http://llimllib.github.io/pymag-trees/)
- [High-performance Tidy Trees - Zxch3n](https://www.zxch3n.com/tidy/tidy/)
- [Radial Tree - Wikipedia](https://en.wikipedia.org/wiki/Radial_tree)

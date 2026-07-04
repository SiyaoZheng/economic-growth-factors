
## Zotero 导入步骤

### 前提：启用 Zotero MCP 写操作
1. 打开 Zotero
2. Tools → Add-ons → Zotero MCP Plugin → Preferences
3. 勾选 "Write Operations"

### 方式一：通过浏览器插件的 Magic Wand 一键导入
大多数候选文献有 DOI 或稳定 URL，在浏览器中打开页面后点击 Zotero Connector 即可导入。

### 方式二：通过 Zotero MCP 的 add_item 逐个导入
启用写操作后，可以使用 MCP 工具逐条添加。

### 方式三：手动创建 collection 并批量导入
1. 在 Zotero 中创建 collection: "AI算力与经济增长"
2. 右键 collection → Add Item by Identifier → 输入 DOI/URL

### 当前状态
- `docs/literature_candidate_discovery.csv`: 24 条候选文献 ✅ (已通过验证)
- `docs/search_queries.md`: 11 路检索记录 ✅
- 24 条中 23 条为 `needs_primary_source`（需打开主页面验证）
- 1 条已在 Zotero 中 (`korinek_2025_gen_ai_econ_research`)

### 下一步（Adrian 需要决策的）
1. 是否启用 Zotero MCP 写操作？
2. 是否需要我将这 24 条文献通过 MCP 逐个添加到 Zotero？
3. 是否需要继续扩充候选文献（如 forward/backward citation chasing）？

# 從 Codebase 生成和優化 Swagger/OpenAPI 的方法

## 📋 目錄
1. [按語言/框架分類的工具](#按語言框架分類的工具)
2. [通用工具](#通用工具)
3. [優化現有 Spec 的方法](#優化現有-spec-的方法)
4. [最佳實踐工作流程](#最佳實踐工作流程)

---

## 按語言/框架分類的工具

### **Node.js / TypeScript**

#### 1. **swagger-jsdoc**
- **方法**: 從 JSDoc 註解生成
- **用法**:
  ```javascript
  /**
   * @swagger
   * /users:
   *   get:
   *     summary: Get all users
   *     responses:
   *       200:
   *         description: Success
   */
  app.get('/users', handler);
  ```
- **優點**: 輕量、與現有註解整合
- **缺點**: 需要手動維護註解

#### 2. **tsoa**
- **方法**: 從 TypeScript 裝飾器生成
- **用法**:
  ```typescript
  @Route("users")
  export class UserController {
    @Get()
    public async getUsers(): Promise<User[]> { }
  }
  ```
- **優點**: 類型安全、自動生成路由和 spec
- **缺點**: 需要使用特定裝飾器語法

#### 3. **NestJS + @nestjs/swagger**
- **方法**: 框架內建支援
- **用法**:
  ```typescript
  @ApiTags('users')
  @Controller('users')
  export class UsersController {
    @Get()
    @ApiOperation({ summary: 'Get all users' })
    findAll() { }
  }
  ```
- **優點**: 無縫整合、自動型別推導
- **工具**: `SwaggerModule.createDocument(app, config)`

#### 4. **fastify-swagger**
- **方法**: 從 JSON Schema 或 route schema 生成
- **優點**: 高效能、與 Fastify 原生整合

#### 5. **routing-controllers-openapi**
- **方法**: 從 routing-controllers 裝飾器生成
- **優點**: 支援 Express/Koa

---

### **Python**

#### 1. **FastAPI** (內建)
- **方法**: 從 Pydantic models + 型別標注自動生成
- **用法**:
  ```python
  @app.get("/users", response_model=List[User])
  async def get_users():
      return users
  ```
- **優點**: 完全自動化、型別安全、零額外配置
- **Spec 位置**: `/docs` (Swagger UI), `/openapi.json`

#### 2. **Flask + flask-restx / flasgger**
- **方法**: 從裝飾器或 YAML 註解生成
- **用法**:
  ```python
  @api.route('/users')
  class UserList(Resource):
      @api.doc('list_users')
      def get(self):
          """List all users"""
  ```

#### 3. **Django + drf-spectacular**
- **方法**: 從 Django REST Framework serializers 生成
- **優點**: 支援複雜的 DRF 功能

#### 4. **apispec**
- **方法**: 從 Marshmallow schemas 生成
- **優點**: 框架無關、靈活

---

### **Java / Spring**

#### 1. **SpringDoc OpenAPI** (Spring Boot 3+)
- **方法**: 從 Spring MVC/WebFlux 註解自動生成
- **用法**:
  ```java
  @Operation(summary = "Get user by ID")
  @GetMapping("/users/{id}")
  public User getUser(@PathVariable Long id) { }
  ```
- **Spec 位置**: `/v3/api-docs`

#### 2. **Springfox** (舊版)
- **方法**: 類似 SpringDoc，但較舊

---

### **Go**

#### 1. **swag**
- **方法**: 從註解生成
- **用法**:
  ```go
  // @Summary Get user
  // @Router /users/{id} [get]
  func GetUser(c *gin.Context) { }
  ```
- **命令**: `swag init`

#### 2. **go-swagger**
- **方法**: 雙向：從 spec 生成 code 或從 code 生成 spec

---

### **C# / .NET**

#### 1. **Swashbuckle** (.NET Core/5+)
- **方法**: 從 ASP.NET Core 控制器自動生成
- **用法**:
  ```csharp
  [HttpGet]
  [ProducesResponseType(typeof(User[]), 200)]
  public IActionResult GetUsers() { }
  ```

#### 2. **NSwag**
- **方法**: 生成 spec + 客戶端程式碼

---

### **PHP**

#### 1. **Laravel + l5-swagger**
- **方法**: 從 PHPDoc 註解生成
- **用法**:
  ```php
  /**
   * @OA\Get(path="/users", ...)
   */
  public function index() { }
  ```

---

## 通用工具

### **1. Reverse Engineering 工具**

#### **swagger-cli / openapi-cli**
- **功能**: 驗證、合併、優化現有 spec
- **用法**:
  ```bash
  swagger-cli validate openapi.yaml
  swagger-cli bundle -o output.yaml input.yaml
  ```

#### **Postman**
- **功能**: 從 API 請求記錄生成 OpenAPI spec
- **方法**: 錄製 API 呼叫 → 導出 OpenAPI

#### **Swagger Inspector**
- **功能**: 從實際 API 呼叫反向生成 spec

#### **APIMatic Transformer**
- **功能**: 轉換不同 API 規格格式
- **支援**: Swagger 2.0 ↔ OpenAPI 3.0 ↔ RAML ↔ Postman

---

### **2. AST/靜態分析工具**

#### **自訂 AST Parser**
- **語言**: 
  - TypeScript: `ts-morph`, `@typescript-eslint/parser`
  - Python: `ast`, `libcst`
  - Java: `JavaParser`
  - Go: `go/ast`
- **方法**: 解析程式碼 → 提取路由、參數、型別 → 生成 spec

#### **範例 (TypeScript + ts-morph)**:
```typescript
import { Project } from 'ts-morph';

const project = new Project();
const sourceFile = project.addSourceFileAtPath('controller.ts');

// 提取所有裝飾器
sourceFile.getClasses().forEach(cls => {
  cls.getMethods().forEach(method => {
    const decorators = method.getDecorators();
    // 分析 @Get, @Post 等
  });
});
```

---

### **3. LLM 輔助生成**

#### **方法 A: Code → Prompt → Spec**
```
提示詞範例：
「分析以下程式碼，生成 OpenAPI 3.0 spec:
[貼上程式碼]
包含：路徑、方法、參數、響應、範例」
```

#### **方法 B: 使用 OpenAI API + 結構化輸出**
```python
import openai

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{
        "role": "system", 
        "content": "You are an OpenAPI spec generator"
    }, {
        "role": "user", 
        "content": f"Generate OpenAPI spec for:\n{code}"
    }],
    response_format={"type": "json_object"}
)
```

---

## 優化現有 Spec 的方法

### **1. 自動優化工具**

#### **Redocly CLI**
```bash
redocly lint openapi.yaml
redocly bundle openapi.yaml -o bundled.yaml
```
- **功能**: Linting、移除重複、優化引用

#### **openapi-generator validate**
```bash
openapi-generator validate -i openapi.yaml
```

#### **Spectral (Stoplight)**
```bash
spectral lint openapi.yaml --ruleset .spectral.yaml
```
- **功能**: 自訂規則、風格檢查

---

### **2. 手動優化檢查清單**

#### **結構優化**
- [ ] 使用 `$ref` 減少重複 schemas
- [ ] 提取共用 components（parameters, responses, schemas）
- [ ] 使用 `allOf` / `oneOf` / `anyOf` 表達繼承關係
- [ ] 定義 `securitySchemes`

#### **文檔品質**
- [ ] 為每個 endpoint 添加 `summary` 和 `description`
- [ ] 為 parameters 添加 `description` 和 `example`
- [ ] 定義完整的 response schemas (200, 400, 401, 500)
- [ ] 添加請求/響應範例

#### **型別精確度**
- [ ] 使用準確的資料型別 (`string`, `integer`, `boolean`, etc.)
- [ ] 添加 `format` (`date-time`, `email`, `uri`, etc.)
- [ ] 設置 `minimum`, `maximum`, `pattern` 等驗證規則
- [ ] 標記必填/選填欄位 (`required`)

#### **Tags & Organization**
- [ ] 使用一致的 `tags` 分組
- [ ] 定義 `tags` 的描述
- [ ] 使用有意義的 `operationId`

#### **範例與文檔**
```yaml
paths:
  /users/{id}:
    get:
      summary: Get user by ID
      description: Retrieves detailed information about a specific user
      tags: [Users]
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
          description: Unique user identifier
          example: 123
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
              example:
                id: 123
                name: "John Doe"
                email: "john@example.com"
        '404':
          $ref: '#/components/responses/NotFound'
```

---

### **3. 自動補全缺失欄位**

#### **使用 LLM**
```python
def optimize_spec(existing_spec):
    missing_fields = detect_missing_descriptions(existing_spec)
    
    for path, method in missing_fields:
        prompt = f"Generate description for {method} {path}"
        description = llm.generate(prompt)
        existing_spec[path][method]['description'] = description
    
    return existing_spec
```

#### **從程式碼推導**
```python
# 從 JSDoc/Docstring 提取描述
def extract_docs_from_code(code_file):
    ast = parse(code_file)
    for function in ast.functions:
        endpoint = extract_route(function)
        description = function.docstring
        # 更新 spec
```

---

## 最佳實踐工作流程

### **方案 A: Code-First (推薦新專案)**
```
1. 選擇支援自動生成的框架
   ├─ FastAPI (Python)
   ├─ NestJS (Node.js)
   └─ SpringDoc (Java)

2. 在程式碼中加入型別/裝飾器
   └─ 使用框架提供的註解 (@ApiOperation, @ApiProperty)

3. 自動生成初始 spec
   └─ 框架內建命令或路由 (/openapi.json)

4. 手動優化
   ├─ 添加 examples
   ├─ 豐富 descriptions
   └─ 定義 error responses

5. 版本控制
   └─ 將 spec 加入 git，設置 CI/CD 驗證
```

### **方案 B: Spec-First (推薦大型團隊)**
```
1. 設計 OpenAPI spec
   └─ 使用 Stoplight Studio / Swagger Editor

2. 驗證 spec
   └─ redocly lint / spectral

3. 從 spec 生成程式碼骨架
   └─ openapi-generator / swagger-codegen

4. 實作業務邏輯
   └─ 填充生成的 stub

5. 保持 spec 與 code 同步
   └─ CI 檢查一致性
```

### **方案 C: 混合式 (現有專案)**
```
1. 掃描現有 codebase
   ├─ AST 解析器
   └─ 或使用反射/元編程

2. 生成基礎 spec
   └─ 自動提取路徑、方法、參數型別

3. 檢查現有 spec (如果有)
   └─ 合併/對比差異

4. LLM 輔助補全
   ├─ 生成 descriptions
   ├─ 添加 examples
   └─ 推測響應格式

5. 人工審查與精煉
   └─ 驗證準確性、添加領域知識

6. 整合到 CI/CD
   ├─ 自動生成文檔
   └─ 破壞性變更檢測
```

---

## 工具推薦矩陣

| 需求 | 推薦工具 | 理由 |
|------|---------|------|
| **從零開始** | FastAPI / NestJS | 自動化程度最高 |
| **已有 Express 專案** | swagger-jsdoc + swagger-ui-express | 侵入性最低 |
| **已有 Spring 專案** | SpringDoc | 原生支援 |
| **現有專案無框架** | AST Parser + LLM | 最靈活 |
| **優化現有 spec** | Redocly + Spectral | 專業級工具 |
| **團隊協作** | Stoplight Studio | 視覺化編輯 |
| **CI/CD 整合** | spectral + redocly CLI | 可自動化 |

---

## 進階技巧

### **自動化流水線**
```yaml
# .github/workflows/openapi.yml
name: OpenAPI
on: [push]
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Generate spec
        run: npm run generate-openapi
      - name: Validate
        run: npx redocly lint openapi.yaml
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: openapi-spec
          path: openapi.yaml
```

### **破壞性變更檢測**
```bash
# 使用 oasdiff
oasdiff breaking old-spec.yaml new-spec.yaml
```

### **多版本管理**
```
/specs
  /v1
    openapi.yaml
  /v2
    openapi.yaml
```

---

## 參考資源

- **OpenAPI 規範**: https://spec.openapis.org/oas/v3.1.0
- **Swagger Editor**: https://editor.swagger.io/
- **Stoplight Studio**: https://stoplight.io/studio
- **Redocly**: https://redocly.com/
- **Spectral 規則**: https://meta.stoplight.io/docs/spectral/

---

## 快速決策樹

```
你的專案是？
├─ 新專案 → 選 Code-First 框架 (FastAPI/NestJS)
├─ 現有專案有框架 → 找對應的 Swagger 套件
├─ 現有專案無框架 → AST Parser 或 LLM 輔助
└─ 已有 spec 要優化 → Redocly + Spectral + 手動精煉
```

---

**建議**: 對於你的需求 (讀 codebase → Swagger，優化現有 spec)：

1. **先檢測語言/框架**
2. **查看是否已有部分 spec**
3. **選擇合適工具**:
   - 有框架 → 用框架內建工具
   - 無框架 → 寫 AST parser 或用 LLM
4. **優化流程**:
   - Spectral 檢測問題
   - LLM 補全描述/範例
   - 手動審查關鍵路徑

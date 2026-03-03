# 從 Codebase 自動生成 Swagger/OpenAPI 文檔 - 研究報告

> **更新日期**: 2026-02-23  
> **研究範圍**: GitHub 上的開源專案和工具

---

## 🎯 研究摘要

本研究調查了網路上現有的「從程式碼自動生成 OpenAPI/Swagger 文檔」的專案和方法。發現主要有三種技術路徑：

1. **框架內建支援** - 從框架原生註解/裝飾器自動生成（最成熟）
2. **註解驅動** - 從 JSDoc/註解解析生成（需手動維護）
3. **AI 驅動靜態分析** - 使用 AST + LLM 分析程式碼（新興方向）

---

## 📦 主要專案分類

### **A. 完全自動化生成（框架支援）**

這類工具與特定框架深度整合，幾乎零配置即可生成完整 OpenAPI spec。

#### **1. FastAPI (Python) - 最佳實踐典範** ⭐⭐⭐⭐⭐
- **GitHub**: https://github.com/tiangolo/fastapi
- **方法**: 從 Pydantic models + 型別標註自動生成
- **優點**:
  - 完全自動化，零額外配置
  - 型別安全，即時驗證
  - 內建 Swagger UI (`/docs`) 和 ReDoc (`/redoc`)
  - OpenAPI 3.0 原生支援
- **範例**:
  ```python
  from fastapi import FastAPI
  from pydantic import BaseModel
  
  app = FastAPI()
  
  class User(BaseModel):
      id: int
      name: str
      email: str
  
  @app.get("/users/{user_id}", response_model=User)
  async def get_user(user_id: int):
      return {"id": user_id, "name": "John", "email": "john@example.com"}
  
  # OpenAPI spec 自動生成在 /openapi.json
  ```
- **適用場景**: Python 新專案、API-first 開發
- **生態系統**: 非常成熟，大量生產環境採用

---

#### **2. NestJS + @nestjs/swagger (TypeScript/Node.js)** ⭐⭐⭐⭐⭐
- **GitHub**: https://github.com/nestjs/swagger
- **方法**: 從裝飾器和型別推導自動生成
- **優點**:
  - 與 NestJS 原生整合
  - 支援 DTO 自動推導
  - 內建 Swagger UI
- **範例**:
  ```typescript
  import { Controller, Get } from '@nestjs/common';
  import { ApiTags, ApiOperation } from '@nestjs/swagger';
  
  @ApiTags('users')
  @Controller('users')
  export class UsersController {
    @Get()
    @ApiOperation({ summary: 'Get all users' })
    findAll(): User[] {
      return [];
    }
  }
  ```
- **適用場景**: TypeScript 企業專案、大型應用
- **Star**: 7.5k+

---

#### **3. drf-spectacular (Django REST Framework)** ⭐⭐⭐⭐⭐
- **GitHub**: https://github.com/tfranzel/drf-spectacular
- **方法**: 從 DRF serializers 和 ViewSets 自動生成
- **優點**:
  - 完整支援 DRF 功能（authentication, pagination, filtering）
  - 自動提取 serializer schemas
  - 支援 polymorphic responses
  - OpenAPI 3.0 & 3.1 支援
- **範例**:
  ```python
  from rest_framework import viewsets
  from drf_spectacular.utils import extend_schema
  
  class UserViewSet(viewsets.ModelViewSet):
      serializer_class = UserSerializer
      
      @extend_schema(
          parameters=[OpenApiParameter(name='status', type=str)],
          responses={200: UserSerializer(many=True)}
      )
      def list(self, request):
          return super().list(request)
  ```
- **適用場景**: Django 專案、成熟的 REST API
- **Star**: 2.3k+
- **特色**: 非常靈活的自訂選項，生產級品質

---

#### **4. SpringDoc OpenAPI (Java/Spring Boot)** ⭐⭐⭐⭐
- **GitHub**: https://github.com/springdoc/springdoc-openapi
- **方法**: 從 Spring MVC/WebFlux 註解自動生成
- **優點**:
  - Spring Boot 3+ 原生支援
  - 自動掃描 @RestController
  - 支援 Spring Security
- **範例**:
  ```java
  @RestController
  @RequestMapping("/users")
  public class UserController {
      @Operation(summary = "Get user by ID")
      @GetMapping("/{id}")
      public User getUser(@PathVariable Long id) {
          return userService.findById(id);
      }
  }
  ```
- **適用場景**: Java 企業應用
- **Star**: 3.1k+

---

### **B. 註解驅動生成**

這類工具需要開發者在程式碼中添加特定格式的註解（JSDoc、PHPDoc 等）。

#### **5. express-jsdoc-swagger (Node.js/Express)** ⭐⭐⭐⭐
- **GitHub**: https://github.com/BRIKEV/express-jsdoc-swagger
- **方法**: 從 JSDoc 註解生成 OpenAPI 3.0
- **優點**:
  - 輕量級，侵入性低
  - 適合現有 Express 專案
  - 內建 Swagger UI
- **範例**:
  ```javascript
  /**
   * GET /api/v1/users
   * @summary Get all users
   * @tags Users
   * @return {array<User>} 200 - success response
   */
  app.get('/api/v1/users', (req, res) => {
    res.json([{ id: 1, name: 'John' }]);
  });
  ```
- **適用場景**: 現有 Express 專案、小型 API
- **Star**: 644+
- **缺點**: 需要手動維護註解，容易與程式碼脫節

---

#### **6. swagger-jsdoc (通用 Node.js)** ⭐⭐⭐⭐
- **GitHub**: https://github.com/Surnet/swagger-jsdoc
- **方法**: 從 JSDoc 註解生成 Swagger 2.0/OpenAPI 3.0
- **優點**:
  - 框架無關，可用於 Express/Koa/Hapi
  - 成熟穩定
- **適用場景**: 通用 Node.js 專案
- **Star**: 5.2k+

---

#### **7. swag (Go)** ⭐⭐⭐⭐
- **GitHub**: https://github.com/swaggo/swag
- **方法**: 從註解生成 Swagger docs
- **範例**:
  ```go
  // @Summary Get user
  // @Description Get user by ID
  // @Tags users
  // @Param id path int true "User ID"
  // @Success 200 {object} User
  // @Router /users/{id} [get]
  func GetUser(c *gin.Context) {
      // ...
  }
  ```
- **命令**: `swag init`
- **適用場景**: Go API 開發
- **Star**: 10.4k+

---

### **C. AI 驅動靜態分析（新興方向）** 🔥

這是最創新的方向，使用 AST 解析 + LLM 分析來自動生成文檔。

#### **8. ApiMesh (qodex-ai) - 重點推薦** ⭐⭐⭐⭐⭐
- **GitHub**: https://github.com/qodex-ai/apimesh
- **方法**: AI 驅動的程式碼掃描 + LLM 生成
- **支援語言**: Python, Node.js, Ruby, Go, Java
- **優點**:
  - **零註解需求** - 直接掃描現有 codebase
  - 自動發現所有 endpoints
  - 生成 OpenAPI 3.0 spec + 互動式 HTML UI
  - 支援多種框架（Django, Flask, FastAPI, Express, NestJS, Rails, Gin）
  - 使用向量嵌入提取上下文資訊
  - 一鍵生成（Docker 或 CLI）
- **工作原理**:
  ```
  1. FileScanner 掃描程式碼（尊重 .gitignore）
  2. 框架檢測（啟發式 + LLM）
  3. 提取 endpoints（原生解析器 + LLM）
  4. 上下文豐富（向量嵌入）
  5. 生成 swagger.json（OpenAI）
  6. 渲染互動式 UI（Swagger UI）
  ```
- **使用方式**:
  ```bash
  # Docker 方式（推薦）
  cd /path/to/your/repo
  docker run --pull always -it --rm -v $(pwd):/workspace qodexai/apimesh:latest
  
  # 輸出檔案：
  # - apimesh/swagger.json
  # - apimesh/apimesh-docs.html（互動式 UI）
  ```
- **適用場景**: 
  - 現有專案無文檔
  - 遺留系統文檔生成
  - 快速原型驗證
- **Star**: 350+（2026年2月更新）
- **特色**: 
  - 自包含 HTML（可離線使用）
  - 支援 CI/CD 整合
  - 可同步到 Qodex.ai 做自動化測試

---

#### **9. Tspec (TypeScript)** ⭐⭐⭐⭐
- **GitHub**: https://github.com/ts-spec/tspec
- **方法**: 從 TypeScript 型別定義生成 OpenAPI
- **優點**:
  - Type-driven（型別驅動）
  - 自動解析 Express/NestJS handler 型別
  - 支援 JSDoc 補充描述
  - 內建 Swagger UI server
- **範例**:
  ```typescript
  import { Tspec } from 'tspec';
  
  interface Book {
    id: number;
    title: string;
  }
  
  export type BookApiSpec = Tspec.DefineApiSpec<{
    paths: {
      '/books/{id}': {
        get: {
          summary: 'Get book by id',
          path: { id: number },
          responses: { 200: Book }
        }
      }
    }
  }>;
  
  // 生成：npx tspec generate --outputPath openapi.json
  ```
- **適用場景**: TypeScript 專案、型別安全需求
- **Star**: 416+
- **特色**: 支援 NestJS 直接掃描 controllers

---

### **D. 反向工程工具**

從實際 API 請求/響應反推 spec。

#### **10. Swagger Inspector / Postman** ⭐⭐⭐
- **方法**: 錄製 API 呼叫，生成 OpenAPI spec
- **優點**: 適合黑箱分析
- **缺點**: 需要手動操作，覆蓋率不完整

---

#### **11. OpenAPI Generator (反向)** ⭐⭐⭐⭐
- **GitHub**: https://github.com/OpenAPITools/openapi-generator
- **Star**: 21.6k+
- **功能**: 主要用於從 spec 生成 code，但也支援驗證和轉換
- **相關**: 可用於優化現有 spec（驗證、bundle、移除重複）

---

### **E. Spec 優化工具**

針對已有的 OpenAPI spec 進行優化和檢查。

#### **12. Redocly CLI** ⭐⭐⭐⭐⭐
- **GitHub**: https://github.com/Redocly/redocly-cli
- **功能**:
  - Linting（語法檢查）
  - Bundle（合併多個 spec）
  - 移除重複定義
  - 優化 `$ref` 引用
- **命令**:
  ```bash
  redocly lint openapi.yaml
  redocly bundle openapi.yaml -o bundled.yaml
  ```
- **適用場景**: 優化現有 spec、CI/CD 整合
- **Star**: 2.3k+

---

#### **13. Spectral (Stoplight)** ⭐⭐⭐⭐⭐
- **GitHub**: https://github.com/stoplightio/spectral
- **功能**:
  - 可自訂規則的 linter
  - 支援 OpenAPI, AsyncAPI, JSON Schema
  - 檢查風格一致性、最佳實踐
- **命令**:
  ```bash
  spectral lint openapi.yaml --ruleset .spectral.yaml
  ```
- **適用場景**: 團隊協作、規範統一
- **Star**: 2.4k+

---

#### **14. oasdiff** ⭐⭐⭐⭐
- **GitHub**: https://github.com/Tufin/oasdiff
- **功能**: 偵測 OpenAPI spec 的破壞性變更
- **命令**:
  ```bash
  oasdiff breaking old-spec.yaml new-spec.yaml
  ```
- **適用場景**: 版本管理、CI/CD 檢查
- **Star**: 814+

---

## 🔬 研究發現與技術趨勢

### **1. 框架整合是主流**
- **最成熟的方案都是框架內建**：FastAPI、NestJS、SpringDoc、drf-spectacular
- **原因**: 框架能直接訪問路由、型別、metadata，生成準確度最高
- **趨勢**: 新框架設計時就考慮 OpenAPI 支援（如 FastAPI）

### **2. AI 驅動分析是新興方向** 🔥
- **代表**: ApiMesh、部分 Tspec 功能
- **優勢**:
  - 適用於無框架/遺留專案
  - 零侵入性
  - 能推測隱式資訊（從變數名、上下文推導）
- **挑戰**:
  - 準確度依賴 LLM 品質
  - 需要 API key（成本）
  - 可能遺漏複雜邏輯

### **3. 型別系統是關鍵**
- **TypeScript/Pydantic/Java Generics 讓自動生成更準確**
- **動態語言（JavaScript, Ruby, PHP）需要更多註解輔助**

### **4. 混合式方法成趨勢**
- **AST 靜態分析 + LLM 語義理解 + 人工審查**
- **範例**: ApiMesh 的 pipeline（Heuristics + Native Parser + LLM）

---

## 🎯 針對不同需求的推薦方案

### **情境 A: 新專案（從零開始）**
| 語言/框架 | 推薦工具 | 理由 |
|-----------|---------|------|
| Python | FastAPI | 零配置，自動化程度最高 |
| TypeScript | NestJS + @nestjs/swagger | 企業級框架 + 原生支援 |
| Node.js (輕量) | express-jsdoc-swagger | 輕量，易上手 |
| Java | SpringDoc OpenAPI | Spring 生態標配 |
| Go | Gin + swag | 成熟工具鏈 |

---

### **情境 B: 現有專案（有框架，無文檔）**
| 現有框架 | 推薦工具 | 工作量 |
|----------|---------|--------|
| Express | express-jsdoc-swagger | 中（需加註解） |
| Django DRF | drf-spectacular | 低（幾乎自動） |
| NestJS | @nestjs/swagger | 低（加裝飾器） |
| Flask | flask-restx / apispec | 中 |
| Spring Boot | SpringDoc | 低 |

---

### **情境 C: 現有專案（無框架/遺留系統）** ⭐
| 需求 | 推薦工具 | 方法 |
|------|---------|------|
| 快速生成 | **ApiMesh** | Docker 一鍵掃描 |
| TypeScript 專案 | Tspec | 型別驅動 |
| 自訂解析 | 自寫 AST Parser + LLM | 最靈活 |

**ApiMesh 特別適合**:
- 遺留程式碼無文檔
- 時間緊迫需要快速生成
- 多語言混合專案

---

### **情境 D: 優化現有 OpenAPI spec**
| 任務 | 推薦工具 | 用途 |
|------|---------|------|
| Linting | Spectral | 檢查規範 |
| 合併/優化 | Redocly CLI | Bundle、去重 |
| 破壞性檢測 | oasdiff | CI/CD 檢查 |
| 補充描述 | LLM (GPT-4) | AI 生成範例和說明 |

---

## 💡 最佳實踐工作流程

### **推薦流程：混合式方法**

```
階段 1: 自動生成基礎 spec
├─ 有框架 → 用框架工具（FastAPI/NestJS/drf-spectacular）
└─ 無框架 → ApiMesh 或 Tspec

階段 2: 靜態檢查與優化
├─ Spectral lint（檢查規範）
├─ Redocly bundle（去重、優化）
└─ oasdiff（版本對比）

階段 3: AI 輔助增強
├─ LLM 生成 descriptions
├─ LLM 生成 examples
└─ LLM 推測缺失的響應格式

階段 4: 人工審查
├─ 驗證關鍵路徑準確性
├─ 補充業務邏輯說明
└─ 添加安全要求

階段 5: 整合到 CI/CD
├─ 自動生成並提交 spec
├─ PR 時自動檢查變更
└─ 破壞性變更警告
```

---

## 🔧 實作建議

### **對於你的需求：讀 codebase → Swagger + 優化**

#### **方案一：快速驗證（推薦優先嘗試）**
使用 **ApiMesh**：
```bash
# 1. 在你的專案目錄執行
cd /path/to/your/project
docker run --pull always -it --rm -v $(pwd):/workspace qodexai/apimesh:latest

# 2. 查看生成的檔案
open apimesh/apimesh-docs.html  # 互動式 UI
cat apimesh/swagger.json        # OpenAPI spec
```

**優點**: 
- 5分鐘內完成
- 零程式碼修改
- 可立即評估效果

---

#### **方案二：框架整合（生產環境推薦）**
如果專案使用常見框架：

**FastAPI**:
```python
from fastapi import FastAPI
app = FastAPI()

# API 自動生成在 /openapi.json
# Swagger UI 在 /docs
```

**NestJS**:
```typescript
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';

const config = new DocumentBuilder()
  .setTitle('API')
  .setVersion('1.0')
  .build();
const document = SwaggerModule.createDocument(app, config);
SwaggerModule.setup('api', app, document);
```

**Express**:
```javascript
const expressJSDocSwagger = require('express-jsdoc-swagger');
expressJSDocSwagger(app)({
  info: { version: '1.0.0', title: 'API' },
  baseDir: __dirname,
  filesPattern: './**/*.js',
});
```

---

#### **方案三：自訂 AST 解析（最靈活）**
適合特殊需求或複雜專案：

**TypeScript 範例**（使用 ts-morph）:
```typescript
import { Project } from 'ts-morph';
import * as yaml from 'js-yaml';

const project = new Project();
const sourceFile = project.addSourceFileAtPath('routes.ts');

const spec = {
  openapi: '3.0.0',
  paths: {}
};

sourceFile.getClasses().forEach(cls => {
  cls.getMethods().forEach(method => {
    const decorators = method.getDecorators();
    const routeDecorator = decorators.find(d => 
      ['Get', 'Post', 'Put', 'Delete'].includes(d.getName())
    );
    
    if (routeDecorator) {
      // 提取路徑、方法、參數、返回型別
      const path = extractPath(routeDecorator);
      const httpMethod = decoratorToMethod(routeDecorator.getName());
      const returnType = method.getReturnType().getText();
      
      spec.paths[path] = {
        [httpMethod]: {
          responses: {
            '200': { description: 'Success' }
          }
        }
      };
    }
  });
});

console.log(yaml.dump(spec));
```

---

#### **方案四：LLM 輔助生成**
使用 GPT-4 分析程式碼：

```python
import openai

code = open('routes.py').read()

prompt = f"""
分析以下程式碼，生成 OpenAPI 3.0 規格：

{code}

要求：
1. 提取所有 API endpoints
2. 推測參數型別
3. 生成完整的 responses
4. 添加 descriptions 和 examples
5. 輸出 JSON 格式
"""

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    response_format={"type": "json_object"}
)

spec = response.choices[0].message.content
```

---

## 📊 工具比較矩陣

| 工具 | 語言支援 | 自動化程度 | 準確度 | 學習曲線 | 適用場景 |
|------|---------|-----------|--------|---------|---------|
| FastAPI | Python | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 新專案 |
| NestJS | TypeScript | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 企業專案 |
| drf-spectacular | Python | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Django |
| ApiMesh | 多語言 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 遺留專案 |
| Tspec | TypeScript | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | TS 專案 |
| express-jsdoc-swagger | Node.js | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | Express |
| swag | Go | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Go API |
| SpringDoc | Java | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Spring |

---

## 🚀 快速決策樹

```
你的專案是？
│
├─ 新專案
│  ├─ Python → FastAPI（零配置）
│  ├─ TypeScript → NestJS + @nestjs/swagger
│  ├─ Node.js → express-jsdoc-swagger
│  ├─ Java → SpringDoc
│  └─ Go → swag
│
├─ 現有專案（有框架）
│  ├─ Django DRF → drf-spectacular
│  ├─ NestJS → 加裝飾器
│  ├─ Express → express-jsdoc-swagger（加註解）
│  └─ Spring → SpringDoc（加註解）
│
├─ 現有專案（無框架/遺留系統）
│  ├─ 快速驗證 → **ApiMesh（Docker 一鍵）**
│  ├─ TypeScript → Tspec
│  └─ 自訂需求 → AST Parser + LLM
│
└─ 優化現有 spec
   ├─ Linting → Spectral
   ├─ 合併優化 → Redocly CLI
   ├─ 變更檢測 → oasdiff
   └─ AI 增強 → GPT-4 補充描述
```

---

## 📚 參考資源

### **官方文檔**
- OpenAPI Spec: https://spec.openapis.org/oas/v3.1.0
- Swagger UI: https://swagger.io/tools/swagger-ui/
- Redoc: https://github.com/Redocly/redoc

### **線上工具**
- Swagger Editor: https://editor.swagger.io/
- Stoplight Studio: https://stoplight.io/studio

### **學習資源**
- OpenAPI Guide: https://swagger.io/docs/specification/
- Awesome OpenAPI: https://github.com/APIs-guru/awesome-openapi3

---

## 🎓 關鍵洞察

### **1. 沒有萬能解法**
- 每個專案的技術棧、架構、成熟度都不同
- 推薦混合多種工具

### **2. 自動化 ≠ 完美**
- 即使最好的工具也無法理解業務邏輯
- 需要人工審查和補充

### **3. 型別系統是基礎**
- 強型別語言（TypeScript, Python type hints）生成效果最好
- 動態語言需要更多手動標註

### **4. AI 是輔助，不是替代**
- LLM 可以補充描述、生成範例
- 但準確性驗證仍需人工

### **5. 持續維護最重要**
- 將 spec 生成整合到 CI/CD
- 每次 code review 同時 review spec
- 使用 oasdiff 偵測破壞性變更

---

## 📌 下一步建議

### **立即行動**
1. **快速驗證**: 用 ApiMesh 掃描你的專案，看效果
2. **評估框架**: 如果有框架，研究對應的內建工具
3. **建立 baseline**: 生成第一版 spec，作為改進基準

### **中期計畫**
1. 補充缺失的 descriptions 和 examples
2. 整合到 CI/CD pipeline
3. 設置 breaking change 檢測

### **長期目標**
1. 建立團隊 OpenAPI 規範（spectral 自訂規則）
2. 自動化生成 SDK 和測試
3. 與 API gateway/監控整合

---

**結論**: 現代工具已經讓「從 codebase 生成 Swagger」變得非常簡單。關鍵是選對工具、設定好流程、持續維護。對於無框架的專案，**ApiMesh** 是革命性的解決方案；對於有框架的專案，用框架內建工具永遠是最優選擇。

---

**最後更新**: 2026-02-23  
**研究者**: Claude (OpenClaw Agent)  
**數據來源**: GitHub, 開發者社群, 官方文檔

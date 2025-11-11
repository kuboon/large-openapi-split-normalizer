# OpenAPI Schema `$ref` 解決の実装方針

## 概要

このドキュメントでは、OpenAPI スキーマファイルにおける `$ref` 参照の仕様と、全ての `$ref` を解決（除去）する実装方針について説明します。

## `$ref` の仕様

### 基本概念

`$ref` は JSON Schema および OpenAPI 仕様において、他のスキーマ定義を参照するための特別なキーワードです。これにより、スキーマの再利用性と保守性が向上します。

### 参照の種類

#### 1. 内部参照（Internal References）

同一ファイル内の別の場所を参照します。

```yaml
# 例: 同一ファイル内のコンポーネント参照
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        name:
          type: string

paths:
  /users:
    get:
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
```

**形式**: `#/path/to/definition`
- `#` は現在のドキュメントのルートを表す
- JSON Pointer 形式でパスを指定

#### 2. 外部参照（External References）

別のファイルを参照します。これは大規模な OpenAPI スキーマで最も重要な形式です。

```yaml
# main.yaml
paths:
  /users:
    get:
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: './schemas/User.yaml'
```

**形式**:
- 相対パス: `./schemas/User.yaml` または `../common/Error.yaml`
- 絶対パス: `/schemas/User.yaml`
- URL: `https://example.com/schemas/User.yaml`

#### 3. 外部参照 + 内部参照の組み合わせ

外部ファイル内の特定の場所を参照します。

```yaml
# 例: 外部ファイルの特定のコンポーネント参照
$ref: './schemas/common.yaml#/components/schemas/Error'
```

### `$ref` の解決ルール

1. **完全置換**: `$ref` を含むオブジェクトは、参照先の定義で完全に置き換えられます
2. **兄弟プロパティ**: OpenAPI 3.0 では `$ref` と同じレベルに他のプロパティがある場合、それらは無視されます（OpenAPI 3.1 では許可される場合があります）
3. **循環参照**: `$ref` が循環参照を形成する可能性があります（例: User → Organization → User）

## 実装方針

### 目標

全ての `$ref` 参照を解決し、単一の自己完結型の OpenAPI スキーマファイルを生成する。

### アーキテクチャ

```
入力: 複数ファイルに分割された OpenAPI スキーマ
  ↓
[1] ファイル読み込みフェーズ
  ↓
[2] 依存関係解析フェーズ
  ↓
[3] 参照解決フェーズ
  ↓
[4] 最適化フェーズ
  ↓
出力: 全ての $ref が解決された統合スキーマ
```

### フェーズ詳細

#### フェーズ 1: ファイル読み込み

**目的**: 全ての関連ファイルをメモリに読み込む

**実装ステップ**:
1. エントリーポイント（メイン OpenAPI ファイル）を特定
2. エントリーポイントを解析し、全ての `$ref` を抽出
3. 外部ファイル参照を検出し、それらのファイルを読み込む
4. 再帰的に、新しく読み込んだファイルの `$ref` を解析
5. 全ての参照されているファイルが読み込まれるまで繰り返す

**データ構造**:
```typescript
interface FileCache {
  [filePath: string]: {
    content: any;        // 解析された YAML/JSON オブジェクト
    refs: string[];      // このファイルが含む全ての $ref
    resolved: boolean;   // 解決済みかどうか
  }
}
```

**注意点**:
- ファイルパスの正規化（相対パスを絶対パスに変換）
- 同じファイルを複数回読み込まないようにキャッシュを使用
- ファイルが見つからない場合のエラーハンドリング

#### フェーズ 2: 依存関係解析

**目的**: ファイル間の依存関係を解析し、解決順序を決定

**実装ステップ**:
1. 全てのファイルと `$ref` から依存関係グラフを構築
2. トポロジカルソートを使用して解決順序を決定
3. 循環依存を検出し、適切に処理

**データ構造**:
```typescript
interface DependencyGraph {
  nodes: Map<string, FileNode>;
  edges: Map<string, Set<string>>;
}

interface FileNode {
  path: string;
  dependencies: Set<string>;  // このファイルが依存する他のファイル
  dependents: Set<string>;    // このファイルに依存している他のファイル
}
```

**循環依存の処理**:
- 循環依存を検出した場合、特別なマーカーを使用
- 後のフェーズで inline 展開せず、参照として保持（または警告）

#### フェーズ 3: 参照解決

**目的**: 全ての `$ref` を実際の定義で置き換える

**実装ステップ**:

1. **ボトムアップ解決**
   - 依存関係のないファイル（リーフノード）から開始
   - 各ファイル内の全ての `$ref` を解決
   - 解決済みのファイルを使って、依存元のファイルを解決

2. **参照解決アルゴリズム**

   ```typescript
   function resolveRef(ref: string, currentFile: string, fileCache: FileCache): any {
     // 1. $ref を解析
     const { filePath, jsonPointer } = parseRef(ref, currentFile);
     
     // 2. 対象ファイルを取得
     const targetFile = fileCache[filePath];
     if (!targetFile) {
       throw new Error(`File not found: ${filePath}`);
     }
     
     // 3. JSON Pointer を使って定義を取得
     const definition = resolveJsonPointer(targetFile.content, jsonPointer);
     
     // 4. 定義内に更に $ref がある場合は再帰的に解決
     return resolveNestedRefs(definition, filePath, fileCache);
   }
   
   function resolveNestedRefs(obj: any, currentFile: string, fileCache: FileCache): any {
     if (typeof obj !== 'object' || obj === null) {
       return obj;
     }
     
     if (obj.$ref) {
       // $ref を解決
       const resolved = resolveRef(obj.$ref, currentFile, fileCache);
       // 解決された定義で置き換え
       return resolveNestedRefs(resolved, currentFile, fileCache);
     }
     
     // オブジェクトまたは配列の全ての子要素を再帰的に処理
     if (Array.isArray(obj)) {
       return obj.map(item => resolveNestedRefs(item, currentFile, fileCache));
     }
     
     const result: any = {};
     for (const [key, value] of Object.entries(obj)) {
       result[key] = resolveNestedRefs(value, currentFile, fileCache);
     }
     return result;
   }
   ```

3. **JSON Pointer の解決**

   ```typescript
   function resolveJsonPointer(obj: any, pointer: string): any {
     if (pointer === '' || pointer === '#') {
       return obj;
     }
     
     // '#/components/schemas/User' → ['components', 'schemas', 'User']
     const parts = pointer.replace(/^#?\//, '').split('/');
     
     let current = obj;
     for (const part of parts) {
       // RFC 6901: エスケープされた文字をデコード
       const decodedPart = part.replace(/~1/g, '/').replace(/~0/g, '~');
       
       if (current === undefined || current === null) {
         throw new Error(`Invalid JSON Pointer: ${pointer}`);
       }
       
       current = current[decodedPart];
     }
     
     return current;
   }
   ```

#### フェーズ 4: 最適化

**目的**: 解決後のスキーマを最適化し、重複を削減

**実装ステップ**:

1. **重複定義の検出**
   - 同一の定義が複数箇所に展開されている場合を検出
   - ハッシュ値を使用して同一性を判定

2. **共通定義の抽出**
   - 重複する定義を `components/schemas` に抽出
   - 内部参照を使用して重複を削減（オプション）

3. **不要な定義の削除**
   - 使用されていない定義を削除（オプション）

### エッジケースの処理

#### 1. 循環参照

**問題**: User → Organization → User のような循環参照

**解決策**:
- オプション A: 循環を検出し、エラーとして報告
- オプション B: 循環を許容し、最大展開深度を設定
- オプション C: 循環部分は内部参照として保持

**推奨**: オプション C - 循環部分は `#/components/schemas/...` として抽出し、内部参照を使用

#### 2. 相対パスの解決

**問題**: 異なるディレクトリ構造での相対パス

**解決策**:
```typescript
function resolveRelativePath(basePath: string, relativePath: string): string {
  // basePath: '/path/to/openapi/schemas/user.yaml'
  // relativePath: '../common/error.yaml'
  // 結果: '/path/to/openapi/common/error.yaml'
  
  const baseDir = path.dirname(basePath);
  return path.resolve(baseDir, relativePath);
}
```

#### 3. 外部 URL 参照

**問題**: HTTP(S) URL での参照

**解決策**:
- ネットワーク経由でファイルを取得
- キャッシュを使用して同じ URL を複数回取得しない
- タイムアウトとエラーハンドリング

#### 4. YAML アンカーとエイリアス

**問題**: YAML の `&anchor` と `*alias` 機能との併用

**解決策**:
- YAML パーサーがアンカー/エイリアスを解決
- その後、`$ref` を解決

### 実装言語とツール

#### MoonBit (WASM) での実装

**利点**:
- クロスプラットフォーム対応（WASM）
- 高速な処理性能
- 型安全性

**実装の主要モジュール**:

```moonbit
// ファイル読み込みと解析
pub struct FileLoader {
  cache: Map[String, FileContent]
}

// 依存関係グラフ
pub struct DependencyGraph {
  nodes: Map[String, FileNode]
  edges: Map[String, Array[String]]
}

// 参照解決エンジン
pub struct RefResolver {
  file_loader: FileLoader
  dep_graph: DependencyGraph
}

// メイン API
pub fn resolve_all_refs(entry_point: String) -> Result[Schema, Error] {
  // 実装
}
```

### テスト戦略

#### 1. ユニットテスト

- JSON Pointer 解決のテスト
- 相対パス解決のテスト
- 循環依存検出のテスト

#### 2. 統合テスト

- シンプルな外部参照の解決
- 複雑な多層参照の解決
- 循環参照を含むケース

#### 3. テストデータセット

```
test-cases/
├── simple/
│   ├── main.yaml          # 1つの外部参照
│   └── schemas/
│       └── User.yaml
├── nested/
│   ├── main.yaml          # 多層の外部参照
│   └── schemas/
│       ├── User.yaml
│       ├── Organization.yaml
│       └── common/
│           └── Error.yaml
└── circular/
    ├── main.yaml          # 循環参照
    └── schemas/
        ├── User.yaml      # → Organization
        └── Organization.yaml  # → User
```

### パフォーマンス考慮事項

1. **メモリ使用量**
   - 大規模スキーマ（100+ ファイル）を想定
   - ストリーミング処理の検討（将来的な最適化）

2. **処理速度**
   - ファイル読み込みのキャッシュ
   - 並列処理の可能性（独立したファイル）

3. **ベンチマーク目標**
   - 100 ファイル: < 1 秒
   - 1000 ファイル: < 10 秒

## 実装のマイルストーン

### フェーズ 1: 基本機能（v0.1）
- [ ] 単一ファイルの内部参照解決
- [ ] シンプルな外部ファイル参照解決
- [ ] 基本的なエラーハンドリング

### フェーズ 2: 高度な機能（v0.2）
- [ ] 多層外部参照の解決
- [ ] 依存関係グラフの構築
- [ ] トポロジカルソート

### フェーズ 3: エッジケース対応（v0.3）
- [ ] 循環参照の検出と処理
- [ ] URL 参照のサポート
- [ ] YAML アンカー/エイリアスとの互換性

### フェーズ 4: 最適化（v0.4）
- [ ] 重複削除
- [ ] パフォーマンス最適化
- [ ] 大規模スキーマでのテスト

## 参考資料

- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [JSON Schema Specification](https://json-schema.org/specification.html)
- [JSON Reference (RFC 3986)](https://tools.ietf.org/html/rfc3986)
- [JSON Pointer (RFC 6901)](https://tools.ietf.org/html/rfc6901)
- [YAML Specification](https://yaml.org/spec/)

## まとめ

この実装方針では、OpenAPI スキーマの全ての `$ref` 参照を解決するための体系的なアプローチを提示しました。主要なポイント:

1. **段階的な処理**: ファイル読み込み → 依存関係解析 → 参照解決 → 最適化
2. **エッジケースへの対応**: 循環参照、外部 URL、相対パスなど
3. **パフォーマンス重視**: キャッシング、効率的なデータ構造
4. **型安全性**: MoonBit の型システムを活用

この方針に従うことで、大規模で複雑な OpenAPI スキーマでも確実に `$ref` を解決できる堅牢なツールを構築できます。

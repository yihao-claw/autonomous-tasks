
import { Project, InterfaceDeclaration, TypeAliasDeclaration, SyntaxKind } from "ts-morph";
import * as path from "path";

// Simplified JSON Schema
interface JsonSchema {
  type?: string;
  properties?: Record<string, JsonSchema>;
  required?: string[];
  items?: JsonSchema;
  enum?: (string | number)[];
  description?: string;
  $ref?: string;
  anyOf?: JsonSchema[];
}

export class SchemaExtractor {
  private project: Project;

  constructor(tsConfigPath?: string) {
    this.project = new Project({
      tsConfigFilePath: tsConfigPath,
      skipAddingFilesFromTsConfig: true, // We add files manually to save memory
    });
  }

  public addFile(filePath: string, content: string) {
    // Overwrite if exists
    const existing = this.project.getSourceFile(filePath);
    if (existing) {
        existing.replaceWithText(content);
    } else {
        this.project.createSourceFile(filePath, content);
    }
  }

  public extractSchemas(filePath: string): Record<string, JsonSchema> {
    const sourceFile = this.project.getSourceFile(filePath);
    if (!sourceFile) return {};

    const schemas: Record<string, JsonSchema> = {};

    // 1. Interfaces
    const interfaces = sourceFile.getInterfaces();
    for (const iface of interfaces) {
      if (iface.isExported()) {
        schemas[iface.getName()] = this.interfaceToSchema(iface);
      }
    }

    // 2. Type Aliases
    const types = sourceFile.getTypeAliases();
    for (const typeAlias of types) {
      if (typeAlias.isExported()) {
        schemas[typeAlias.getName()] = this.typeToSchema(typeAlias);
      }
    }

    return schemas;
  }

  private interfaceToSchema(iface: InterfaceDeclaration): JsonSchema {
    const schema: JsonSchema = { type: "object", properties: {}, required: [] };
    const props = iface.getProperties();

    for (const prop of props) {
      const name = prop.getName();
      const typeNode = prop.getTypeNode();
      const isOptional = prop.hasQuestionToken();
      const jsDoc = prop.getJsDocs()[0]?.getDescription().trim();

      if (!isOptional) {
        schema.required?.push(name);
      }

      // Basic Type mapping (Enhanced logic would go deep here)
      const propSchema = this.mapTypeToSchema(typeNode?.getText() || "any");
      if (jsDoc) propSchema.description = jsDoc;

      if (schema.properties) {
        schema.properties[name] = propSchema;
      }
    }
    
    // Interface-level JSDoc
    const ifaceDoc = iface.getJsDocs()[0]?.getDescription().trim();
    if (ifaceDoc) schema.description = ifaceDoc;

    return schema;
  }

  private typeToSchema(typeAlias: TypeAliasDeclaration): JsonSchema {
    const typeNode = typeAlias.getTypeNode();
    const schema = this.mapTypeToSchema(typeNode?.getText() || "any");
    
    const doc = typeAlias.getJsDocs()[0]?.getDescription().trim();
    if (doc) schema.description = doc;
    
    return schema;
  }

  private mapTypeToSchema(typeText: string): JsonSchema {
    // Very basic mapping for V1
    if (typeText === "string") return { type: "string" };
    if (typeText === "number") return { type: "number" };
    if (typeText === "boolean") return { type: "boolean" };
    if (typeText.endsWith("[]")) {
        return { 
            type: "array", 
            items: this.mapTypeToSchema(typeText.slice(0, -2)) 
        };
    }
    // Handle array<T>
    if (typeText.startsWith("Array<")) {
        const inner = typeText.slice(6, -1);
        return { type: "array", items: this.mapTypeToSchema(inner) };
    }
    
    // Assume it's a reference if it starts with uppercase (heuristic)
    if (/^[A-Z]/.test(typeText)) {
        return { $ref: `#/components/schemas/${typeText}` };
    }

    return { type: "string", description: `TODO: Complex type (${typeText})` }; // Fallback
  }
}

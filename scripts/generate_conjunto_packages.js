const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const args = process.argv.slice(2);

function argument(name) {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : null;
}

if (args.includes("--help")) {
  console.log(
    "Usage: node scripts/generate_conjunto_packages.js " +
      "[--shared <shared-parameters.txt>] [--output <directory>]",
  );
  process.exit(0);
}

const defaultSharedName = "SUP-.parametros-compartilhados-bim-trivia_ATUALIZADO.txt";
const sharedPath = path.resolve(
  argument("--shared") ||
    (fs.existsSync(path.join(process.cwd(), defaultSharedName))
      ? path.join(process.cwd(), defaultSharedName)
      : path.join(root, defaultSharedName)),
);
const conjunto = path.resolve(argument("--output") || path.join(process.cwd(), "Conjunto"));
const today = new Date().toISOString().slice(0, 10);

if (!fs.existsSync(sharedPath)) {
  throw new Error(
    `Shared parameters file not found: ${sharedPath}. Use --shared <file>.`,
  );
}

fs.mkdirSync(conjunto, { recursive: true });

const xmlEscape = (value) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");

const shared = new Map();
for (const line of fs.readFileSync(sharedPath, "utf8").split(/\r?\n/)) {
  if (!line.startsWith("PARAM\t")) continue;
  const parts = line.split("\t");
  shared.set(parts[2], {
    guid: parts[1],
    name: parts[2],
    datatype: parts[3],
    group: parts[5],
    description: parts[7] || "",
  });
}

const category = {
  Walls: ["-2000011", "Walls"],
  Floors: ["-2000032", "Floors"],
  Doors: ["-2000023", "Doors"],
  Windows: ["-2000014", "Windows"],
  Roofs: ["-2000035", "Roofs"],
  Ceilings: ["-2000038", "Ceilings"],
  Stairs: ["-2000120", "Stairs"],
  Runs: ["-2000919", "Runs"],
  Railings: ["-2000126", "Stairs Railings"],
  PlumbingFixtures: ["-2001160", "Plumbing Fixtures"],
  Furniture: ["-2000080", "Furniture"],
  SpecialtyEquipment: ["-2001350", "Specialty Equipment"],
  Planting: ["-2001360", "Planting"],
  Site: ["-2001260", "Site"],
  Ramps: ["-2000180", "Ramps"],
  SlabEdges: ["-2001392", "Slab Edges"],
  CurtainPanels: ["-2000170", "Curtain Panels"],
  CurtainMullions: ["-2000171", "Curtain Wall Mullions"],
  StructuralFoundations: ["-2001300", "Structural Foundations"],
  StructuralFraming: ["-2001320", "Structural Framing"],
  StructuralColumns: ["-2001330", "Structural Columns"],
};

const groupNames = {
  "5": "Dados Basicos",
  "9": "Arquitetura",
  "11": "Estrutura",
  "15": "Paisagismo",
};

const unitMeta = {
  TEXT: ["Text", "autodesk.spec:spec.string-2.0.0", "Text"],
  LENGTH: ["Double", "autodesk.spec.aec:length-2.0.1", "Length"],
  AREA: ["Double", "autodesk.spec.aec:area-2.0.1", "Area"],
  VOLUME: ["Double", "autodesk.spec.aec:volume-2.0.1", "Volume"],
  NUMBER: ["Double", "autodesk.spec.aec:number-2.0.1", "Number"],
  SLOPE: ["Double", "autodesk.spec.aec:slope-2.0.1", "Slope"],
  MATERIAL: ["ElementId", "autodesk.revit.category:ost_materials-1.0.0", "Material"],
  YESNO: ["Boolean", "autodesk.spec:spec.bool-1.0.0", "Yes/No"],
  FORCE: ["Double", "autodesk.spec.aec:force-2.0.1", "Force"],
};

function sharedXml(name, categories, isInstance) {
  const p = shared.get(name);
  if (!p) throw new Error(`Shared parameter not found: ${name}`);
  const meta = unitMeta[p.datatype];
  if (!meta) throw new Error(`Unsupported datatype ${p.datatype} for ${name}`);
  const categoryXml = categories
    .map((key) => {
      const value = category[key];
      if (!value) throw new Error(`Unknown Revit category: ${key}`);
      return `        <Category ID="${value[0]}" Name="${value[1]}" />`;
    })
    .join("\n");
  return `    <Parameter GUID="${p.guid}" Name="${xmlEscape(p.name)}" Group="${xmlEscape(groupNames[p.group] || p.group)}" Type="${meta[0]}" UnitType="${meta[1]}" UnitTypeDisplay="${meta[2]}" Description="${xmlEscape(p.description)}" IsInstance="${isInstance ? "True" : "False"}" GroupUnder="autodesk.parameter.group:data-1.0.0" AlignGroupValues="True" UserModifiable="True" HideWhenNoValue="False">
      <Categories>
${categoryXml}
      </Categories>
    </Parameter>`;
}

function interoperabilityXml(name, description, bindings) {
  return `<?xml version="1.0" encoding="utf-8"?>
<SharedParametersConfig Version="10.0" Name="${xmlEscape(name)} ${today}" Author="" Description="${xmlEscape(description)}" Image="">
  <Parameters>
${bindings.map((b) => sharedXml(b.name, b.categories, b.instance)).join("\n")}
  </Parameters>
</SharedParametersConfig>
`;
}

function psetBlock(name, entity, properties) {
  return `PropertySet:\t${name}\tT\t${entity}
${properties.map((p) => `\t${p[0]}\t${p[1]}\t${p[2]}`).join("\n")}`;
}

function identificationBlocks(entities) {
  return entities.map((entity) =>
    psetBlock("SUP_Identification", entity, [
      ["CodigoPP", "Text", "CodigoPP"],
      ["Pset_compor", "Text", "Pset_compor"],
      ["CodigoTrivia", "Text", "CODIGO TRIVIA"],
    ])
  );
}

function writePsets(file, discipline, blocks, notes = []) {
  const text = [
    `# REVIT IFC USER DEFINED PROPERTY SETS - ${discipline.toUpperCase()}`,
    "# Schema alvo: IFC2X3",
    "# Somente propriedades customizadas. Quantidades e materiais nativos nao sao duplicados.",
    "# Psets customizados usam prefixo SUP_; o prefixo Pset_ e reservado a definicoes oficiais.",
    ...notes.map((n) => `# ${n}`),
    "",
    blocks.join("\n\n"),
    "",
  ].join("\n");
  fs.writeFileSync(path.join(conjunto, file), text, "utf8");
}

function valueNode(value, indent) {
  return `${" ".repeat(indent)}<simpleValue>${xmlEscape(value)}</simpleValue>`;
}

function restrictedNode(values, indent) {
  if (values.length === 1) return valueNode(values[0], indent);
  return `${" ".repeat(indent)}<xs:restriction base="xs:string">
${values.map((v) => `${" ".repeat(indent + 2)}<xs:enumeration value="${xmlEscape(v)}" />`).join("\n")}
${" ".repeat(indent)}</xs:restriction>`;
}

function entityFacet(entities, predefinedType) {
  return `        <entity>
          <name>
${restrictedNode(entities, 12)}
          </name>${predefinedType ? `
          <predefinedType>
${restrictedNode(Array.isArray(predefinedType) ? predefinedType : [predefinedType], 12)}
          </predefinedType>` : ""}
        </entity>`;
}

function propertyRequirement(pset, name, dataType = "IFCTEXT") {
  return `        <property cardinality="required" dataType="${dataType}">
          <propertySet>
            <simpleValue>${xmlEscape(pset)}</simpleValue>
          </propertySet>
          <baseName>
            <simpleValue>${xmlEscape(name)}</simpleValue>
          </baseName>
        </property>`;
}

function attributeRequirement(name) {
  return `        <attribute cardinality="required">
          <name>
            <simpleValue>${xmlEscape(name)}</simpleValue>
          </name>
        </attribute>`;
}

function specification({ name, entities, predefinedType, requirements, instructions = "" }) {
  return `    <specification name="${xmlEscape(name)}" ifcVersion="IFC2X3"${instructions ? ` instructions="${xmlEscape(instructions)}"` : ""}>
      <applicability minOccurs="0" maxOccurs="unbounded">
${entityFacet(entities, predefinedType)}
      </applicability>
      <requirements>
${requirements.join("\n")}
      </requirements>
    </specification>`;
}

function writeIds(file, title, description, specifications) {
  const text = `<?xml version="1.0" encoding="utf-8"?>
<ids xmlns="http://standards.buildingsmart.org/IDS" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://standards.buildingsmart.org/IDS https://standards.buildingsmart.org/IDS/1.0/ids.xsd">
  <info>
    <title>${xmlEscape(title)}</title>
    <description>${xmlEscape(description)}</description>
    <author>borgeslimamodeler@gmail.com</author>
    <date>${today}</date>
  </info>
  <specifications>
${specifications.join("\n")}
  </specifications>
</ids>
`;
  fs.writeFileSync(path.join(conjunto, file), text, "utf8");
}

const genericBonsai = [
  ["class", "IFC Class"],
  ["PredefinedType", "PredefinedType"],
  ["ObjectType", "ObjectType"],
  ["type.Name", "Tipo"],
  ["container.Name", "Nivel"],
  ["material.Name", "Material"],
  ["*.CodigoPP", "CodigoPP"],
];

function writeBonsai(file, query, fields) {
  const attributes = [...genericBonsai, ...fields].map(([name, header]) => ({
    name,
    header,
    sort: "NONE",
    group: "NONE",
    summary: "NONE",
    formatting: "{{value}}",
  }));
  const content = {
    query,
    attributes,
    settings: {
      should_generate_svg: false,
      should_preserve_existing: false,
      include_global_id: true,
      null_value: "0",
      empty_value: "-",
      true_value: "YES",
      false_value: "NO",
      concat_value: ",",
      csv_delimiter: ";",
      format: "xlsx",
      csv_custom_delimiter: "",
    },
  };
  fs.writeFileSync(path.join(conjunto, file), `${JSON.stringify(content, null, 2)}\n`, "utf8");
}

const architectureEntities = [
  "IfcWall", "IfcWallStandardCase", "IfcSlab", "IfcCovering", "IfcDoor", "IfcWindow",
  "IfcRoof", "IfcStair", "IfcStairFlight", "IfcRailing", "IfcCurtainWall",
  "IfcFlowTerminal", "IfcFurnishingElement", "IfcElementAssembly",
  "IfcBuildingElementProxy", "IfcRamp", "IfcMember",
];

const architecturePsets = [
  ...identificationBlocks(architectureEntities),
  psetBlock("SUP_WallProperties", "IfcWall", [
    ["Revestimento", "Text", "Revestimento"],
    ["IsWetArea", "Boolean", "SUP_AreaMolhada"],
  ]),
  psetBlock("SUP_WallProperties", "IfcWallStandardCase", [
    ["Revestimento", "Text", "Revestimento"],
    ["IsWetArea", "Boolean", "SUP_AreaMolhada"],
  ]),
  psetBlock("SUP_FloorFinish", "IfcCovering", [
    ["FinishType", "Text", "TipoDeAcabamento"],
    ["MechanicalResistance", "Text", "ResistenciaMecanica"],
  ]),
  psetBlock("SUP_CeilingProperties", "IfcCovering", [
    ["MoistureResistance", "Text", "ResistenciaAUmidade"],
    ["CeilingType", "Text", "TipoDeForro"],
  ]),
  ...["IfcWall", "IfcSlab", "IfcRoof"].map((e) =>
    psetBlock("SUP_Waterproofing", e, [["SystemType", "Text", "TipoDeSistema"]])
  ),
  psetBlock("SUP_RoofProperties", "IfcRoof", [
    ["RoofType", "Text", "TipoDeCobertura"],
    ["MoistureResistance", "Text", "ResistenciaAUmidade"],
  ]),
  ...["IfcStair", "IfcStairFlight"].map((e) =>
    psetBlock("SUP_StairProperties", e, [
      ["AssemblyPlace", "Text", "LocalDeMontagemEscada"],
      ["StrengthClass", "Text", "ClasseDeResistenciaEscada"],
    ])
  ),
  ...["IfcRailing", "IfcCurtainWall"].map((e) =>
    psetBlock("SUP_RailingProperties", e, [
      ["ClosureType", "Text", "TipoDeFechamento"],
      ["FixingType", "Text", "TipoDeFixacao"],
      ["MechanicalResistance", "Text", "ResistenciaMecanicaGuardaCorpo"],
    ])
  ),
  psetBlock("SUP_Vegetation", "IfcBuildingElementProxy", [
    ["Species", "Text", "EspecieVegetal"],
  ]),
  ...["IfcMember", "IfcBuildingElementProxy"].map((e) =>
    psetBlock("SUP_Kerb", e, [
      ["Type", "Text", "TipoMeioFio"],
      ["CombinedWithGutter", "Boolean", "CombinadoComSarjeta"],
      ["IsTraversable", "Boolean", "Transponivel"],
      ["AssemblyPlace", "Text", "LocalDeMontagem"],
      ["StrengthClass", "Text", "ClasseDeResistencia"],
    ])
  ),
];

writePsets(
  "revit_user_defined_psets_arquitetura.txt",
  "Arquitetura",
  architecturePsets,
  [
    "Impermeabilizacao permanece como camada dos elementos hospedeiros.",
    "Quantidades customizadas devem ser geradas como IfcElementQuantity e sao validadas pelo IDS.",
  ]
);

const architectureBindings = [
  { name: "CodigoPP", categories: ["Walls", "Floors", "Doors", "Windows", "Roofs", "Ceilings", "Stairs", "Runs", "Railings", "PlumbingFixtures", "Furniture", "SpecialtyEquipment", "Planting", "Site", "Ramps", "SlabEdges", "CurtainPanels", "CurtainMullions"], instance: false },
  { name: "Pset_compor", categories: ["Walls", "Floors", "Doors", "Windows", "Roofs", "Ceilings", "Stairs", "Runs", "Railings", "PlumbingFixtures", "Furniture", "SpecialtyEquipment", "Planting", "Site", "Ramps", "SlabEdges", "CurtainPanels", "CurtainMullions"], instance: false },
  { name: "CODIGO TRIVIA", categories: ["Walls", "Floors", "Doors", "Windows", "Roofs", "Ceilings", "Stairs", "Runs", "Railings", "PlumbingFixtures", "Furniture", "SpecialtyEquipment", "Planting", "Site", "Ramps", "SlabEdges", "CurtainPanels", "CurtainMullions"], instance: false },
  { name: "Revestimento", categories: ["Walls"], instance: false },
  { name: "SUP_AreaMolhada", categories: ["Walls"], instance: true },
  { name: "AreaCalculada", categories: ["Walls", "Floors", "Roofs", "Ceilings"], instance: true },
  { name: "Perimetro", categories: ["Floors", "Roofs", "Ceilings"], instance: true },
  { name: "Espessura", categories: ["Walls", "Floors", "Roofs", "Ceilings"], instance: false },
  { name: "TipoDeAcabamento", categories: ["Floors"], instance: false },
  { name: "ResistenciaMecanica", categories: ["Floors"], instance: false },
  { name: "ResistenciaAUmidade", categories: ["Roofs", "Ceilings"], instance: false },
  { name: "TipoDeForro", categories: ["Ceilings"], instance: false },
  { name: "SUP_InclinacaoForro", categories: ["Ceilings"], instance: true },
  { name: "TipoDeSistema", categories: ["Walls", "Floors", "Roofs"], instance: false },
  { name: "TipoDeCobertura", categories: ["Roofs"], instance: false },
  { name: "SUP_VolumePorta", categories: ["Doors"], instance: true },
  { name: "SUP_VolumeCaixilho", categories: ["Windows"], instance: true },
  { name: "AlturaEscada", categories: ["Stairs"], instance: true },
  { name: "LarguraEscada", categories: ["Stairs", "Runs"], instance: false },
  { name: "EspessuraPisoEscada", categories: ["Stairs", "Runs"], instance: false },
  { name: "EspessuraEspelhoEscada", categories: ["Stairs", "Runs"], instance: false },
  { name: "LocalDeMontagemEscada", categories: ["Stairs", "Runs"], instance: false },
  { name: "ClasseDeResistenciaEscada", categories: ["Stairs", "Runs"], instance: false },
  { name: "TipoDeFechamento", categories: ["Railings", "CurtainPanels", "CurtainMullions"], instance: false },
  { name: "TipoDeFixacao", categories: ["Railings", "CurtainPanels", "CurtainMullions"], instance: false },
  { name: "ResistenciaMecanicaGuardaCorpo", categories: ["Railings", "CurtainPanels", "CurtainMullions"], instance: false },
  { name: "AlturaMudaNumerica", categories: ["Planting"], instance: false },
  { name: "Largura", categories: ["Planting", "SlabEdges", "Site"], instance: false },
  { name: "Altura", categories: ["Planting", "SlabEdges", "Site"], instance: false },
  { name: "Comprimento", categories: ["SlabEdges", "Site"], instance: true },
  { name: "DiametroDaCopa", categories: ["Planting"], instance: false },
  { name: "EspecieVegetal", categories: ["Planting"], instance: false },
  { name: "TipoMeioFio", categories: ["SlabEdges", "Site"], instance: false },
  { name: "SUP_ResistenciaCompressao", categories: ["SlabEdges", "Site"], instance: false },
  { name: "LocalDeMontagem", categories: ["SlabEdges", "Site"], instance: false },
  { name: "CombinadoComSarjeta", categories: ["SlabEdges", "Site"], instance: false },
  { name: "Transponivel", categories: ["SlabEdges", "Site"], instance: false },
  { name: "Status", categories: ["Walls", "Floors", "Doors", "Windows", "Roofs", "Ceilings", "Stairs", "Railings", "SlabEdges", "Site"], instance: true },
];

fs.writeFileSync(
  path.join(conjunto, "export_interbility_tools_arquitetura.xml"),
  interoperabilityXml("Arquitetura", "Parametros compartilhados aprovados de Arquitetura.", architectureBindings),
  "utf8"
);

const architectureSpecs = [
  specification({
    name: "Arquitetura - CodigoPP",
    entities: architectureEntities.map((e) => e.toUpperCase()),
    requirements: [propertyRequirement("SUP_Identification", "CodigoPP")],
    instructions: "Resultado 0/0 deve ser reportado como ausencia de cobertura.",
  }),
  specification({
    name: "Paredes - quantidades e area molhada",
    entities: ["IFCWALL", "IFCWALLSTANDARDCASE"],
    requirements: [
      propertyRequirement("BaseQuantities", "Height", "IFCLENGTHMEASURE"),
      propertyRequirement("BaseQuantities", "Width", "IFCLENGTHMEASURE"),
      propertyRequirement("BaseQuantities", "NetSideArea", "IFCAREAMEASURE"),
      propertyRequirement("SUP_WallProperties", "IsWetArea", "IFCBOOLEAN"),
    ],
  }),
  specification({
    name: "Pisos - quantidades",
    entities: ["IFCSLAB"],
    requirements: [
      propertyRequirement("BaseQuantities", "NominalWidth", "IFCLENGTHMEASURE"),
      propertyRequirement("BaseQuantities", "NetArea", "IFCAREAMEASURE"),
      propertyRequirement("BaseQuantities", "NetVolume", "IFCVOLUMEMEASURE"),
    ],
  }),
  specification({
    name: "Portas - dimensoes",
    entities: ["IFCDOOR"],
    requirements: [attributeRequirement("OverallHeight"), attributeRequirement("OverallWidth")],
  }),
  specification({
    name: "Janelas - dimensoes",
    entities: ["IFCWINDOW"],
    requirements: [attributeRequirement("OverallHeight"), attributeRequirement("OverallWidth")],
  }),
  specification({
    name: "Forros - classificacao e area",
    entities: ["IFCCOVERING"],
    predefinedType: "CEILING",
    requirements: [
      propertyRequirement("BaseQuantities", "NetArea", "IFCAREAMEASURE"),
      propertyRequirement("SUP_CeilingProperties", "CeilingType"),
    ],
  }),
  specification({
    name: "Coberturas - tipo",
    entities: ["IFCROOF"],
    requirements: [propertyRequirement("SUP_RoofProperties", "RoofType")],
  }),
  specification({
    name: "Escadas - quantidades",
    entities: ["IFCSTAIR", "IFCSTAIRFLIGHT"],
    requirements: [
      propertyRequirement("SUP_StairQuantities", "Height", "IFCLENGTHMEASURE"),
      propertyRequirement("SUP_StairQuantities", "Width", "IFCLENGTHMEASURE"),
    ],
  }),
  specification({
    name: "Guarda-corpos - dados",
    entities: ["IFCRAILING"],
    requirements: [
      propertyRequirement("SUP_RailingQuantities", "Length", "IFCLENGTHMEASURE"),
      propertyRequirement("SUP_RailingProperties", "ClosureType"),
      propertyRequirement("SUP_RailingProperties", "FixingType"),
    ],
  }),
  specification({
    name: "Vegetacao - dados",
    entities: ["IFCBUILDINGELEMENTPROXY"],
    requirements: [
      propertyRequirement("SUP_Vegetation", "Species"),
      propertyRequirement("SUP_VegetationQuantities", "Height", "IFCLENGTHMEASURE"),
    ],
  }),
  specification({
    name: "Meio-fio - dados",
    entities: ["IFCMEMBER", "IFCBUILDINGELEMENTPROXY"],
    requirements: [
      propertyRequirement("SUP_Kerb", "Type"),
      propertyRequirement("SUP_KerbQuantities", "Length", "IFCLENGTHMEASURE"),
    ],
  }),
];

writeIds(
  "ids_arquitetura.ids",
  "Trivia BIM - Arquitetura",
  "Validacao da disciplina Arquitetura em IFC2X3. Resultado 0/0 nao comprova atendimento.",
  architectureSpecs
);

writeBonsai("bonsai_csv_config_arquitetura.json", "IfcProduct", [
  ["BaseQuantities.Height", "Altura"],
  ["BaseQuantities.Width", "Espessura"],
  ["BaseQuantities.NetArea", "Area liquida"],
  ["BaseQuantities.NetSideArea", "Area lateral liquida"],
  ["BaseQuantities.NetVolume", "Volume liquido"],
  ["SUP_WallProperties.IsWetArea", "Parede - Area molhada"],
  ["SUP_WallProperties.Revestimento", "Parede - Revestimento"],
  ["SUP_FloorFinish.FinishType", "Piso - Acabamento"],
  ["SUP_CeilingProperties.CeilingType", "Forro - Tipo"],
  ["SUP_RoofProperties.RoofType", "Cobertura - Tipo"],
  ["SUP_Waterproofing.SystemType", "Impermeabilizacao - Sistema"],
  ["OverallHeight", "Porta/Janela - Altura"],
  ["OverallWidth", "Porta/Janela - Largura"],
  ["SUP_StairQuantities.Height", "Escada - Altura"],
  ["SUP_StairQuantities.Width", "Escada - Largura"],
  ["SUP_RailingQuantities.Length", "Guarda-corpo - Comprimento"],
  ["SUP_RailingProperties.ClosureType", "Guarda-corpo - Fechamento"],
  ["SUP_Vegetation.Species", "Vegetacao - Especie"],
  ["SUP_VegetationQuantities.Height", "Vegetacao - Altura"],
  ["SUP_Kerb.Type", "Meio-fio - Tipo"],
  ["SUP_KerbQuantities.Length", "Meio-fio - Comprimento"],
]);

const concretePsets = [
  ...["IfcWall", "IfcFooting", "IfcBeam"].map((e) =>
    psetBlock("SUP_StructuralMaterials", e, [["BeddingMaterial", "Text", "MaterialLastro"]])
  ),
  psetBlock("SUP_PileProperties", "IfcPile", [
    ["ExecutionMethod", "Text", "SUP_TipoExecucaoEstaca"],
    ["DesignLoadCapacity", "Force", "SUP_CapacidadeCargaEstaca"],
  ]),
];

writePsets(
  "revit_user_defined_psets_concreto.txt",
  "Estrutura de Concreto",
  concretePsets,
  [
    "Codigos, descricoes, fases e materiais estruturais nativos nao sao duplicados.",
    "Quantidades customizadas devem ser geradas como IfcElementQuantity e sao validadas pelo IDS.",
  ]
);

const structuralCategories = ["Walls", "StructuralFoundations", "StructuralFraming", "StructuralColumns", "Floors", "Stairs", "Runs"];
const concreteBindings = [
  { name: "AreaDeForma", categories: ["Walls", "StructuralFoundations", "StructuralFraming", "StructuralColumns", "Floors"], instance: true },
  { name: "Altura", categories: ["Walls", "StructuralFoundations"], instance: true },
  { name: "Largura", categories: ["StructuralFoundations"], instance: false },
  { name: "Comprimento", categories: structuralCategories, instance: true },
  { name: "Volume", categories: structuralCategories, instance: true },
  { name: "VolumeLastro", categories: ["Walls", "StructuralFoundations", "StructuralFraming"], instance: true },
  { name: "MaterialLastro", categories: ["Walls", "StructuralFoundations", "StructuralFraming"], instance: false },
  { name: "EspessuraLastro", categories: ["Walls", "StructuralFoundations", "StructuralFraming"], instance: false },
  { name: "VolumeEscavacao", categories: ["StructuralFoundations", "StructuralFraming"], instance: true },
  { name: "DiametroEstaca", categories: ["StructuralFoundations"], instance: false },
  { name: "SUP_TipoExecucaoEstaca", categories: ["StructuralFoundations"], instance: false },
  { name: "SUP_CapacidadeCargaEstaca", categories: ["StructuralFoundations"], instance: false },
  { name: "LarguraSecaoPilar", categories: ["StructuralColumns"], instance: false },
  { name: "ProfundidadeSecaoPilar", categories: ["StructuralColumns"], instance: false },
  { name: "LarguraSecaoViga", categories: ["StructuralFraming"], instance: false },
  { name: "AlturaSecaoViga", categories: ["StructuralFraming"], instance: false },
  { name: "LarguraLaje", categories: ["Floors"], instance: false },
  { name: "ComprimentoLaje", categories: ["Floors"], instance: false },
];

fs.writeFileSync(
  path.join(conjunto, "export_interbility_tools_concreto.xml"),
  interoperabilityXml("Estrutura de Concreto", "Parametros compartilhados aprovados da estrutura de concreto.", concreteBindings),
  "utf8"
);

const concreteSpecs = [
  specification({
    name: "Muros e paredes estruturais",
    entities: ["IFCWALL", "IFCWALLSTANDARDCASE"],
    requirements: [
      propertyRequirement("BaseQuantities", "Height", "IFCLENGTHMEASURE"),
      propertyRequirement("BaseQuantities", "Length", "IFCLENGTHMEASURE"),
      propertyRequirement("BaseQuantities", "NetVolume", "IFCVOLUMEMEASURE"),
      propertyRequirement("SUP_WallQuantities", "FormworkArea", "IFCAREAMEASURE"),
    ],
  }),
  specification({
    name: "Sapatas e blocos de fundacao",
    entities: ["IFCFOOTING"],
    requirements: [
      propertyRequirement("SUP_FootingQuantities", "Width", "IFCLENGTHMEASURE"),
      propertyRequirement("SUP_FootingQuantities", "Height", "IFCLENGTHMEASURE"),
      propertyRequirement("SUP_FootingQuantities", "Length", "IFCLENGTHMEASURE"),
      propertyRequirement("SUP_FootingQuantities", "NetVolume", "IFCVOLUMEMEASURE"),
      propertyRequirement("SUP_FootingQuantities", "FormworkArea", "IFCAREAMEASURE"),
    ],
  }),
  specification({
    name: "Estacas",
    entities: ["IFCPILE"],
    requirements: [
      propertyRequirement("BaseQuantities", "Length", "IFCLENGTHMEASURE"),
      propertyRequirement("SUP_PileQuantities", "Diameter", "IFCLENGTHMEASURE"),
      propertyRequirement("SUP_PileQuantities", "NetVolume", "IFCVOLUMEMEASURE"),
      propertyRequirement("SUP_PileProperties", "ExecutionMethod"),
      propertyRequirement("SUP_PileProperties", "DesignLoadCapacity", "IFCFORCEMEASURE"),
    ],
  }),
  specification({
    name: "Vigas e baldrames",
    entities: ["IFCBEAM"],
    requirements: [
      propertyRequirement("BaseQuantities", "Length", "IFCLENGTHMEASURE"),
      propertyRequirement("SUP_BeamQuantities", "Width", "IFCLENGTHMEASURE"),
      propertyRequirement("SUP_BeamQuantities", "Height", "IFCLENGTHMEASURE"),
      propertyRequirement("SUP_BeamQuantities", "NetVolume", "IFCVOLUMEMEASURE"),
      propertyRequirement("SUP_BeamQuantities", "FormworkArea", "IFCAREAMEASURE"),
    ],
  }),
  specification({
    name: "Pilares",
    entities: ["IFCCOLUMN"],
    requirements: [
      propertyRequirement("BaseQuantities", "NominalLength", "IFCLENGTHMEASURE"),
      propertyRequirement("BaseQuantities", "NetVolume", "IFCVOLUMEMEASURE"),
      propertyRequirement("SUP_ColumnQuantities", "Width", "IFCLENGTHMEASURE"),
      propertyRequirement("SUP_ColumnQuantities", "Depth", "IFCLENGTHMEASURE"),
      propertyRequirement("SUP_ColumnQuantities", "FormworkArea", "IFCAREAMEASURE"),
    ],
  }),
  specification({
    name: "Lajes",
    entities: ["IFCSLAB"],
    requirements: [
      propertyRequirement("BaseQuantities", "NominalWidth", "IFCLENGTHMEASURE"),
      propertyRequirement("BaseQuantities", "NetArea", "IFCAREAMEASURE"),
      propertyRequirement("BaseQuantities", "NetVolume", "IFCVOLUMEMEASURE"),
      propertyRequirement("SUP_SlabQuantities", "FormworkArea", "IFCAREAMEASURE"),
    ],
  }),
  specification({
    name: "Escadas estruturais",
    entities: ["IFCSTAIRFLIGHT"],
    requirements: [
      propertyRequirement("SUP_StairFlightQuantities", "Length", "IFCLENGTHMEASURE"),
      propertyRequirement("SUP_StairFlightQuantities", "NetVolume", "IFCVOLUMEMEASURE"),
    ],
  }),
];

writeIds(
  "ids_concreto.ids",
  "Trivia BIM - Estrutura de Concreto",
  "Validacao da estrutura de concreto em IFC2X3. Resultado 0/0 nao comprova atendimento.",
  concreteSpecs
);

writeBonsai("bonsai_csv_config_concreto.json", "IfcProduct", [
  ["BaseQuantities.Length", "Comprimento"],
  ["BaseQuantities.Height", "Altura"],
  ["BaseQuantities.Width", "Espessura"],
  ["BaseQuantities.NominalWidth", "Espessura nominal"],
  ["BaseQuantities.NominalLength", "Comprimento nominal"],
  ["BaseQuantities.NetArea", "Area liquida"],
  ["BaseQuantities.NetVolume", "Volume liquido"],
  ["SUP_WallQuantities.FormworkArea", "Parede - Area de forma"],
  ["SUP_WallQuantities.BeddingVolume", "Parede - Volume lastro"],
  ["SUP_FootingQuantities.FormworkArea", "Fundacao - Area de forma"],
  ["SUP_FootingQuantities.Width", "Fundacao - Largura"],
  ["SUP_FootingQuantities.Height", "Fundacao - Altura"],
  ["SUP_FootingQuantities.Length", "Fundacao - Comprimento"],
  ["SUP_FootingQuantities.NetVolume", "Fundacao - Volume"],
  ["SUP_FootingQuantities.BeddingVolume", "Fundacao - Volume lastro"],
  ["SUP_FootingQuantities.ExcavationVolume", "Fundacao - Volume escavacao"],
  ["SUP_PileQuantities.Diameter", "Estaca - Diametro"],
  ["SUP_PileQuantities.NetVolume", "Estaca - Volume"],
  ["SUP_PileProperties.ExecutionMethod", "Estaca - Metodo executivo"],
  ["SUP_PileProperties.DesignLoadCapacity", "Estaca - Capacidade carga"],
  ["SUP_BeamQuantities.FormworkArea", "Viga - Area de forma"],
  ["SUP_BeamQuantities.Width", "Viga - Largura"],
  ["SUP_BeamQuantities.Height", "Viga - Altura"],
  ["SUP_BeamQuantities.NetVolume", "Viga - Volume"],
  ["SUP_ColumnQuantities.FormworkArea", "Pilar - Area de forma"],
  ["SUP_ColumnQuantities.Width", "Pilar - Largura"],
  ["SUP_ColumnQuantities.Depth", "Pilar - Profundidade"],
  ["SUP_SlabQuantities.FormworkArea", "Laje - Area de forma"],
  ["SUP_StairFlightQuantities.Length", "Escada - Comprimento lance"],
  ["SUP_StairFlightQuantities.NetVolume", "Escada - Volume lance"],
  ["SUP_StructuralMaterials.BeddingMaterial", "Material lastro"],
]);

console.log("Generated architecture and concrete packages.");

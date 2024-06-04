# WorkflowNo_1270
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1270
doc: A workflow including the tool(s) MaxQuant, CrosstalkDB, PRIDE Toolsuite, XTandemPipeline, Quant.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3913" # Loom
  input_2:
    type: File
    format: "http://edamontology.org/format_3620" # xlsx
  input_3:
    type: File
    format: "http://edamontology.org/format_3652" # dta
steps:
  MaxQuant_01:
    run: add-path-to-the-implementation/MaxQuant.cwl 
    in:
      MaxQuant_in_1: input_2
    out: [MaxQuant_out_1, MaxQuant_out_2]
  CrosstalkDB_02:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: MaxQuant_01/MaxQuant_out_1
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  PRIDE Toolsuite_03:
    run: add-path-to-the-implementation/PRIDE Toolsuite.cwl 
    in:
      PRIDE Toolsuite_in_1: CrosstalkDB_02/CrosstalkDB_out_3
    out: [PRIDE Toolsuite_out_1]
  XTandemPipeline_04:
    run: add-path-to-the-implementation/XTandemPipeline.cwl 
    in:
      XTandemPipeline_in_1: PRIDE Toolsuite_03/PRIDE Toolsuite_out_1
    out: [XTandemPipeline_out_1, XTandemPipeline_out_2]
  Quant_05:
    run: add-path-to-the-implementation/Quant.cwl 
    in:
      Quant_in_1: input_3
      Quant_in_2: XTandemPipeline_04/XTandemPipeline_out_1
    out: [Quant_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3468" # xls
    outputSource: Quant_05/Quant_out_1

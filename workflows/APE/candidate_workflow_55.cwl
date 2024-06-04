# WorkflowNo_54
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_54
doc: A workflow including the tool(s) PRIDE Toolsuite, CrosstalkDB, XTandemPipeline, OpenMS, ComplexBrowser.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3752" # CSV
  input_2:
    type: File
    format: "http://edamontology.org/format_3711" # X!Tandem XML
  input_3:
    type: File
    format: "http://edamontology.org/format_3244" # mzML
steps:
  PRIDE Toolsuite_01:
    run: add-path-to-the-implementation/PRIDE Toolsuite.cwl 
    in:
      PRIDE Toolsuite_in_1: input_3
    out: [PRIDE Toolsuite_out_1]
  CrosstalkDB_02:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: input_1
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  XTandemPipeline_03:
    run: add-path-to-the-implementation/XTandemPipeline.cwl 
    in:
      XTandemPipeline_in_1: input_2
    out: [XTandemPipeline_out_1, XTandemPipeline_out_2]
  OpenMS_04:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: PRIDE Toolsuite_01/PRIDE Toolsuite_out_1
      OpenMS_in_2: input_3
      OpenMS_in_3: XTandemPipeline_03/XTandemPipeline_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  ComplexBrowser_05:
    run: add-path-to-the-implementation/ComplexBrowser.cwl 
    in:
      ComplexBrowser_in_1: OpenMS_04/OpenMS_out_2
      ComplexBrowser_in_2: CrosstalkDB_02/CrosstalkDB_out_1
    out: [ComplexBrowser_out_1, ComplexBrowser_out_2, ComplexBrowser_out_3]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3508" # PDF
    outputSource: ComplexBrowser_05/ComplexBrowser_out_1

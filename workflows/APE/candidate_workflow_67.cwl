# WorkflowNo_66
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_66
doc: A workflow including the tool(s) XTandemPipeline, Multi-Q, msmsEDA, CrosstalkDB, ComplexBrowser.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3711" # X!Tandem XML
  input_2:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
  input_3:
    type: File
    format: "http://edamontology.org/format_3650" # netCDF
steps:
  XTandemPipeline_01:
    run: add-path-to-the-implementation/XTandemPipeline.cwl 
    in:
      XTandemPipeline_in_1: input_1
    out: [XTandemPipeline_out_1, XTandemPipeline_out_2]
  Multi-Q_02:
    run: add-path-to-the-implementation/Multi-Q.cwl 
    in:
      Multi-Q_in_1: input_2
      Multi-Q_in_2: XTandemPipeline_01/XTandemPipeline_out_1
    out: [Multi-Q_out_1]
  msmsEDA_03:
    run: add-path-to-the-implementation/msmsEDA.cwl 
    in:
      msmsEDA_in_1: input_3
    out: [msmsEDA_out_1, msmsEDA_out_2, msmsEDA_out_3]
  CrosstalkDB_04:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: Multi-Q_02/Multi-Q_out_1
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  ComplexBrowser_05:
    run: add-path-to-the-implementation/ComplexBrowser.cwl 
    in:
      ComplexBrowser_in_1: msmsEDA_03/msmsEDA_out_3
      ComplexBrowser_in_2: CrosstalkDB_04/CrosstalkDB_out_1
    out: [ComplexBrowser_out_1, ComplexBrowser_out_2, ComplexBrowser_out_3]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3508" # PDF
    outputSource: ComplexBrowser_05/ComplexBrowser_out_1

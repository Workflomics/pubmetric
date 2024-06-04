# WorkflowNo_1213
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1213
doc: A workflow including the tool(s) CrosstalkDB, esimsa, OpenSWATH, MS-Fit, Multi-Q.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_2002" # srs format
  input_2:
    type: File
    format: "http://edamontology.org/format_3752" # CSV
  input_3:
    type: File
    format: "http://edamontology.org/format_1504" # aaindex
steps:
  CrosstalkDB_01:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: input_2
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  esimsa_02:
    run: add-path-to-the-implementation/esimsa.cwl 
    in:
      esimsa_in_1: input_3
      esimsa_in_2: input_1
      esimsa_in_3: input_1
    out: [esimsa_out_1, esimsa_out_2, esimsa_out_3]
  OpenSWATH_03:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: CrosstalkDB_01/CrosstalkDB_out_3
    out: [OpenSWATH_out_1]
  MS-Fit_04:
    run: add-path-to-the-implementation/MS-Fit.cwl 
    in:
      MS-Fit_in_1: esimsa_02/esimsa_out_2
    out: [MS-Fit_out_1]
  Multi-Q_05:
    run: add-path-to-the-implementation/Multi-Q.cwl 
    in:
      Multi-Q_in_1: OpenSWATH_03/OpenSWATH_out_1
      Multi-Q_in_2: MS-Fit_04/MS-Fit_out_1
    out: [Multi-Q_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3311" # RNAML
    outputSource: Multi-Q_05/Multi-Q_out_1

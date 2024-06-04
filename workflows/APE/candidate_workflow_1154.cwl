# WorkflowNo_1153
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1153
doc: A workflow including the tool(s) CrosstalkDB, MSiReader, CPM, MS-Fit, Quant.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3752" # CSV
  input_2:
    type: File
    format: "http://edamontology.org/format_3652" # dta
  input_3:
    type: File
    format: "http://edamontology.org/format_1216" # unambiguous pure rna sequence
steps:
  CrosstalkDB_01:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: input_1
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  MSiReader_02:
    run: add-path-to-the-implementation/MSiReader.cwl 
    in:
      MSiReader_in_1: input_3
      MSiReader_in_2: CrosstalkDB_01/CrosstalkDB_out_3
    out: [MSiReader_out_1, MSiReader_out_2]
  CPM_03:
    run: add-path-to-the-implementation/CPM.cwl 
    in:
      CPM_in_1: MSiReader_02/MSiReader_out_2
      CPM_in_2: input_3
    out: [CPM_out_1, CPM_out_2]
  MS-Fit_04:
    run: add-path-to-the-implementation/MS-Fit.cwl 
    in:
      MS-Fit_in_1: CPM_03/CPM_out_2
    out: [MS-Fit_out_1]
  Quant_05:
    run: add-path-to-the-implementation/Quant.cwl 
    in:
      Quant_in_1: input_2
      Quant_in_2: MS-Fit_04/MS-Fit_out_1
    out: [Quant_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3468" # xls
    outputSource: Quant_05/Quant_out_1

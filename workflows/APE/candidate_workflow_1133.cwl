# WorkflowNo_1132
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1132
doc: A workflow including the tool(s) msmsEDA, MSiReader, DeconMSn, ComPIL, isobar.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3913" # Loom
  input_2:
    type: File
    format: "http://edamontology.org/format_3712" # Thermo RAW
  input_3:
    type: File
    format: "http://edamontology.org/format_3609" # qualillumina
steps:
  msmsEDA_01:
    run: add-path-to-the-implementation/msmsEDA.cwl 
    in:
      msmsEDA_in_1: input_2
    out: [msmsEDA_out_1, msmsEDA_out_2, msmsEDA_out_3]
  MSiReader_02:
    run: add-path-to-the-implementation/MSiReader.cwl 
    in:
      MSiReader_in_1: input_3
      MSiReader_in_2: msmsEDA_01/msmsEDA_out_3
    out: [MSiReader_out_1, MSiReader_out_2]
  DeconMSn_03:
    run: add-path-to-the-implementation/DeconMSn.cwl 
    in:
      DeconMSn_in_1: input_2
      DeconMSn_in_2: input_2
    out: [DeconMSn_out_1, DeconMSn_out_2, DeconMSn_out_3]
  ComPIL_04:
    run: add-path-to-the-implementation/ComPIL.cwl 
    in:
      ComPIL_in_1: MSiReader_02/MSiReader_out_2
    out: [ComPIL_out_1]
  isobar_05:
    run: add-path-to-the-implementation/isobar.cwl 
    in:
      isobar_in_1: DeconMSn_03/DeconMSn_out_1
      isobar_in_2: ComPIL_04/ComPIL_out_1
    out: [isobar_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3508" # PDF
    outputSource: isobar_05/isobar_out_1

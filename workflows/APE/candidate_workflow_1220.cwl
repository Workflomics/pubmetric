# WorkflowNo_1217
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1217
doc: A workflow including the tool(s) Peppy, OpenMS, ASAPRatio, OpenSWATH, PEAKS DB.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3652" # dta
  input_2:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
  input_3:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
steps:
  Peppy_01:
    run: add-path-to-the-implementation/Peppy.cwl 
    in:
      Peppy_in_1: input_1
      Peppy_in_2: input_3
      Peppy_in_3: input_2
    out: [Peppy_out_1, Peppy_out_2]
  OpenMS_02:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_1
      OpenMS_in_2: input_3
      OpenMS_in_3: Peppy_01/Peppy_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  ASAPRatio_03:
    run: add-path-to-the-implementation/ASAPRatio.cwl 
    in:
      ASAPRatio_in_1: OpenMS_02/OpenMS_out_1
    out: [ASAPRatio_out_1, ASAPRatio_out_2]
  OpenSWATH_04:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: ASAPRatio_03/ASAPRatio_out_2
    out: [OpenSWATH_out_1]
  PEAKS DB_05:
    run: add-path-to-the-implementation/PEAKS DB.cwl 
    in:
      PEAKS DB_in_1: OpenSWATH_04/OpenSWATH_out_1
      PEAKS DB_in_2: input_2
    out: [PEAKS DB_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_2311" # EMBL-HTML
    outputSource: PEAKS DB_05/PEAKS DB_out_1

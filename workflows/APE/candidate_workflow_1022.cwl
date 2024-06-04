# WorkflowNo_1021
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1021
doc: A workflow including the tool(s) OpenChrom, msmsEDA, MSiReader, XTandemPipeline, OpenMS.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_2352" # BioXSD (XML)
  input_2:
    type: File
    format: "http://edamontology.org/format_3650" # netCDF
  input_3:
    type: File
    format: "http://edamontology.org/format_3713" # Mascot .dat file
steps:
  OpenChrom_01:
    run: add-path-to-the-implementation/OpenChrom.cwl 
    in:
      OpenChrom_in_1: input_2
    out: [OpenChrom_out_1, OpenChrom_out_2]
  msmsEDA_02:
    run: add-path-to-the-implementation/msmsEDA.cwl 
    in:
      msmsEDA_in_1: input_2
    out: [msmsEDA_out_1, msmsEDA_out_2, msmsEDA_out_3]
  MSiReader_03:
    run: add-path-to-the-implementation/MSiReader.cwl 
    in:
      MSiReader_in_1: OpenChrom_01/OpenChrom_out_1
      MSiReader_in_2: msmsEDA_02/msmsEDA_out_2
    out: [MSiReader_out_1, MSiReader_out_2]
  XTandemPipeline_04:
    run: add-path-to-the-implementation/XTandemPipeline.cwl 
    in:
      XTandemPipeline_in_1: input_3
    out: [XTandemPipeline_out_1, XTandemPipeline_out_2]
  OpenMS_05:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: MSiReader_03/MSiReader_out_2
      OpenMS_in_2: input_1
      OpenMS_in_3: XTandemPipeline_04/XTandemPipeline_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3652" # dta
    outputSource: OpenMS_05/OpenMS_out_1

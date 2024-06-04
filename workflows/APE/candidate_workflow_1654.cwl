# WorkflowNo_1653
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1653
doc: A workflow including the tool(s) msmsEDA, MSiReader, ComPIL, IsobariQ, MSiReader.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3650" # netCDF
  input_2:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
  input_3:
    type: File
    format: "http://edamontology.org/format_3244" # mzML
steps:
  msmsEDA_01:
    run: add-path-to-the-implementation/msmsEDA.cwl 
    in:
      msmsEDA_in_1: input_1
    out: [msmsEDA_out_1, msmsEDA_out_2, msmsEDA_out_3]
  MSiReader_02:
    run: add-path-to-the-implementation/MSiReader.cwl 
    in:
      MSiReader_in_1: input_3
      MSiReader_in_2: msmsEDA_01/msmsEDA_out_3
    out: [MSiReader_out_1, MSiReader_out_2]
  ComPIL_03:
    run: add-path-to-the-implementation/ComPIL.cwl 
    in:
      ComPIL_in_1: MSiReader_02/MSiReader_out_2
    out: [ComPIL_out_1]
  IsobariQ_04:
    run: add-path-to-the-implementation/IsobariQ.cwl 
    in:
      IsobariQ_in_1: ComPIL_03/ComPIL_out_1
    out: [IsobariQ_out_1]
  MSiReader_05:
    run: add-path-to-the-implementation/MSiReader.cwl 
    in:
      MSiReader_in_1: input_2
      MSiReader_in_2: IsobariQ_04/IsobariQ_out_1
    out: [MSiReader_out_1, MSiReader_out_2]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3592" # BMP
    outputSource: MSiReader_05/MSiReader_out_1

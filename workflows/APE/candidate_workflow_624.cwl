# WorkflowNo_623
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_623
doc: A workflow including the tool(s) PGConverter, MSiReader, MS-Fit, OpenMS, OpenSWATH.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3956" # N-Quads
  input_2:
    type: File
    format: "http://edamontology.org/format_3652" # dta
  input_3:
    type: File
    format: "http://edamontology.org/format_3827" # proBED
steps:
  PGConverter_01:
    run: add-path-to-the-implementation/PGConverter.cwl 
    in:
      PGConverter_in_1: input_3
    out: [PGConverter_out_1]
  MSiReader_02:
    run: add-path-to-the-implementation/MSiReader.cwl 
    in:
      MSiReader_in_1: PGConverter_01/PGConverter_out_1
      MSiReader_in_2: input_1
    out: [MSiReader_out_1, MSiReader_out_2]
  MS-Fit_03:
    run: add-path-to-the-implementation/MS-Fit.cwl 
    in:
      MS-Fit_in_1: input_3
    out: [MS-Fit_out_1]
  OpenMS_04:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: MSiReader_02/MSiReader_out_2
      OpenMS_in_2: input_2
      OpenMS_in_3: MS-Fit_03/MS-Fit_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  OpenSWATH_05:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: OpenMS_04/OpenMS_out_2
    out: [OpenSWATH_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
    outputSource: OpenSWATH_05/OpenSWATH_out_1

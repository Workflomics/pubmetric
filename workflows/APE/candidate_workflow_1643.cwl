# WorkflowNo_1642
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1642
doc: A workflow including the tool(s) BioLCCC, PeptideProphet, OpenMS, Jtraml, MSiReader.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_1628" # ABI
  input_2:
    type: File
    format: "http://edamontology.org/format_2549" # OBO
  input_3:
    type: File
    format: "http://edamontology.org/format_3311" # RNAML
steps:
  BioLCCC_01:
    run: add-path-to-the-implementation/BioLCCC.cwl 
    in:
      BioLCCC_in_1: input_2
    out: [BioLCCC_out_1]
  PeptideProphet_02:
    run: add-path-to-the-implementation/PeptideProphet.cwl 
    in:
      PeptideProphet_in_1: BioLCCC_01/BioLCCC_out_1
    out: [PeptideProphet_out_1]
  OpenMS_03:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_3
      OpenMS_in_2: input_2
      OpenMS_in_3: PeptideProphet_02/PeptideProphet_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  Jtraml_04:
    run: add-path-to-the-implementation/Jtraml.cwl 
    in:
      Jtraml_in_1: input_1
    out: [Jtraml_out_1]
  MSiReader_05:
    run: add-path-to-the-implementation/MSiReader.cwl 
    in:
      MSiReader_in_1: Jtraml_04/Jtraml_out_1
      MSiReader_in_2: OpenMS_03/OpenMS_out_2
    out: [MSiReader_out_1, MSiReader_out_2]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3591" # TIFF
    outputSource: MSiReader_05/MSiReader_out_1

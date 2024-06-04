# WorkflowNo_1404
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1404
doc: A workflow including the tool(s) mzStar, MyriMatch, OpenMS, RelEx, PChopper.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3710" # WIFF format
  input_2:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
  input_3:
    type: File
    format: "http://edamontology.org/format_3311" # RNAML
steps:
  mzStar_01:
    run: add-path-to-the-implementation/mzStar.cwl 
    in:
      mzStar_in_1: input_1
    out: [mzStar_out_1]
  MyriMatch_02:
    run: add-path-to-the-implementation/MyriMatch.cwl 
    in:
      MyriMatch_in_1: input_1
      MyriMatch_in_2: input_2
    out: [MyriMatch_out_1]
  OpenMS_03:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_3
      OpenMS_in_2: mzStar_01/mzStar_out_1
      OpenMS_in_3: MyriMatch_02/MyriMatch_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  RelEx_04:
    run: add-path-to-the-implementation/RelEx.cwl 
    in:
      RelEx_in_1: OpenMS_03/OpenMS_out_1
    out: [RelEx_out_1]
  PChopper_05:
    run: add-path-to-the-implementation/PChopper.cwl 
    in:
      PChopper_in_1: RelEx_04/RelEx_out_1
    out: [PChopper_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_2532" # GenBank-HTML
    outputSource: PChopper_05/PChopper_out_1

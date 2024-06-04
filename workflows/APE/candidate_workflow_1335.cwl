# WorkflowNo_1334
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1334
doc: A workflow including the tool(s) dig, MyriMatch, OpenMS, RelEx, MS-Isotope.

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
  dig_01:
    run: add-path-to-the-implementation/dig.cwl 
    in:
      dig_in_1: input_2
    out: [dig_out_1]
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
      OpenMS_in_2: dig_01/dig_out_1
      OpenMS_in_3: MyriMatch_02/MyriMatch_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  RelEx_04:
    run: add-path-to-the-implementation/RelEx.cwl 
    in:
      RelEx_in_1: OpenMS_03/OpenMS_out_1
    out: [RelEx_out_1]
  MS-Isotope_05:
    run: add-path-to-the-implementation/MS-Isotope.cwl 
    in:
      MS-Isotope_in_1: RelEx_04/RelEx_out_1
    out: [MS-Isotope_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_2532" # GenBank-HTML
    outputSource: MS-Isotope_05/MS-Isotope_out_1

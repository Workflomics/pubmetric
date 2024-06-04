# WorkflowNo_63
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_63
doc: A workflow including the tool(s) MS-Isotope, XTandem Parser, InDigestion, MS-GF+, OpenMS.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3653" # pkl
  input_2:
    type: File
    format: "http://edamontology.org/format_1957" # raw
  input_3:
    type: File
    format: "http://edamontology.org/format_3711" # X!Tandem XML
steps:
  MS-Isotope_01:
    run: add-path-to-the-implementation/MS-Isotope.cwl 
    in:
      MS-Isotope_in_1: input_2
    out: [MS-Isotope_out_1]
  XTandem Parser_02:
    run: add-path-to-the-implementation/XTandem Parser.cwl 
    in:
      XTandem Parser_in_1: input_3
    out: [XTandem Parser_out_1, XTandem Parser_out_2]
  InDigestion_03:
    run: add-path-to-the-implementation/InDigestion.cwl 
    in:
      InDigestion_in_1: input_2
    out: [InDigestion_out_1, InDigestion_out_2, InDigestion_out_3]
  MS-GF+_04:
    run: add-path-to-the-implementation/MS-GF+.cwl 
    in:
      MS-GF+_in_1: input_1
      MS-GF+_in_2: InDigestion_03/InDigestion_out_3
    out: [MS-GF+_out_1, MS-GF+_out_2]
  OpenMS_05:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: XTandem Parser_02/XTandem Parser_out_2
      OpenMS_in_2: MS-Isotope_01/MS-Isotope_out_1
      OpenMS_in_3: MS-GF+_04/MS-GF+_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
    outputSource: OpenMS_05/OpenMS_out_1

# WorkflowNo_16
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_16
doc: A workflow including the tool(s) MS-Isotope, InDigestion, protk, Percolator, OpenMS.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_1957" # raw
  input_2:
    type: File
    format: "http://edamontology.org/format_3651" # MGF
  input_3:
    type: File
    format: "http://edamontology.org/format_3655" # pepXML
steps:
  MS-Isotope_01:
    run: add-path-to-the-implementation/MS-Isotope.cwl 
    in:
      MS-Isotope_in_1: input_1
    out: [MS-Isotope_out_1]
  InDigestion_02:
    run: add-path-to-the-implementation/InDigestion.cwl 
    in:
      InDigestion_in_1: input_1
    out: [InDigestion_out_1, InDigestion_out_2, InDigestion_out_3]
  protk_03:
    run: add-path-to-the-implementation/protk.cwl 
    in:
      protk_in_1: InDigestion_02/InDigestion_out_3
      protk_in_2: input_3
    out: [protk_out_1, protk_out_2]
  Percolator_04:
    run: add-path-to-the-implementation/Percolator.cwl 
    in:
      Percolator_in_1: protk_03/protk_out_1
    out: [Percolator_out_1]
  OpenMS_05:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: MS-Isotope_01/MS-Isotope_out_1
      OpenMS_in_2: input_2
      OpenMS_in_3: Percolator_04/Percolator_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
    outputSource: OpenMS_05/OpenMS_out_1

# WorkflowNo_714
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_714
doc: A workflow including the tool(s) InDigestion, MR-MSPOLYGRAPH, MR-MSPOLYGRAPH, MassWiz, isobar.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3651" # MGF
  input_2:
    type: File
    format: "http://edamontology.org/format_3652" # dta
  input_3:
    type: File
    format: "http://edamontology.org/format_1960" # Staden format
steps:
  InDigestion_01:
    run: add-path-to-the-implementation/InDigestion.cwl 
    in:
      InDigestion_in_1: input_3
    out: [InDigestion_out_1, InDigestion_out_2, InDigestion_out_3]
  MR-MSPOLYGRAPH_02:
    run: add-path-to-the-implementation/MR-MSPOLYGRAPH.cwl 
    in:
      MR-MSPOLYGRAPH_in_1: input_2
      MR-MSPOLYGRAPH_in_2: InDigestion_01/InDigestion_out_3
    out: [MR-MSPOLYGRAPH_out_1, MR-MSPOLYGRAPH_out_2]
  MR-MSPOLYGRAPH_03:
    run: add-path-to-the-implementation/MR-MSPOLYGRAPH.cwl 
    in:
      MR-MSPOLYGRAPH_in_1: MR-MSPOLYGRAPH_02/MR-MSPOLYGRAPH_out_2
      MR-MSPOLYGRAPH_in_2: InDigestion_01/InDigestion_out_3
    out: [MR-MSPOLYGRAPH_out_1, MR-MSPOLYGRAPH_out_2]
  MassWiz_04:
    run: add-path-to-the-implementation/MassWiz.cwl 
    in:
      MassWiz_in_1: MR-MSPOLYGRAPH_03/MR-MSPOLYGRAPH_out_2
    out: [MassWiz_out_1]
  isobar_05:
    run: add-path-to-the-implementation/isobar.cwl 
    in:
      isobar_in_1: input_1
      isobar_in_2: MassWiz_04/MassWiz_out_1
    out: [isobar_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3468" # xls
    outputSource: isobar_05/isobar_out_1

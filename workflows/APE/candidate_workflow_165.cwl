# WorkflowNo_164
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_164
doc: A workflow including the tool(s) InDigestion, MR-MSPOLYGRAPH, make_random, PEAKS DB, PEAKS Q.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3827" # proBED
  input_2:
    type: File
    format: "http://edamontology.org/format_3652" # dta
  input_3:
    type: File
    format: "http://edamontology.org/format_2310" # FASTA-HTML
steps:
  InDigestion_01:
    run: add-path-to-the-implementation/InDigestion.cwl 
    in:
      InDigestion_in_1: input_1
    out: [InDigestion_out_1, InDigestion_out_2, InDigestion_out_3]
  MR-MSPOLYGRAPH_02:
    run: add-path-to-the-implementation/MR-MSPOLYGRAPH.cwl 
    in:
      MR-MSPOLYGRAPH_in_1: input_2
      MR-MSPOLYGRAPH_in_2: InDigestion_01/InDigestion_out_3
    out: [MR-MSPOLYGRAPH_out_1, MR-MSPOLYGRAPH_out_2]
  make_random_03:
    run: add-path-to-the-implementation/make_random.cwl 
    in:
      make_random_in_1: input_3
    out: [make_random_out_1]
  PEAKS DB_04:
    run: add-path-to-the-implementation/PEAKS DB.cwl 
    in:
      PEAKS DB_in_1: MR-MSPOLYGRAPH_02/MR-MSPOLYGRAPH_out_2
      PEAKS DB_in_2: make_random_03/make_random_out_1
    out: [PEAKS DB_out_1, PEAKS DB_out_2]
  PEAKS Q_05:
    run: add-path-to-the-implementation/PEAKS Q.cwl 
    in:
      PEAKS Q_in_1: PEAKS DB_04/PEAKS DB_out_1
    out: [PEAKS Q_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_2311" # EMBL-HTML
    outputSource: PEAKS Q_05/PEAKS Q_out_1

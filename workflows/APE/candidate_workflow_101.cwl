# WorkflowNo_100
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_100
doc: A workflow including the tool(s) InDigestion, CrosstalkDB, PRIDE Toolsuite, PECAN (PEptide-Centric Analysis), Mascot Server.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3752" # CSV
  input_2:
    type: File
    format: "http://edamontology.org/format_3882" # PSF
  input_3:
    type: File
    format: "http://edamontology.org/format_3244" # mzML
steps:
  InDigestion_01:
    run: add-path-to-the-implementation/InDigestion.cwl 
    in:
      InDigestion_in_1: input_2
    out: [InDigestion_out_1, InDigestion_out_2, InDigestion_out_3]
  CrosstalkDB_02:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: input_1
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  PRIDE Toolsuite_03:
    run: add-path-to-the-implementation/PRIDE Toolsuite.cwl 
    in:
      PRIDE Toolsuite_in_1: CrosstalkDB_02/CrosstalkDB_out_4
    out: [PRIDE Toolsuite_out_1]
  PECAN (PEptide-Centric Analysis)_04:
    run: add-path-to-the-implementation/PECAN (PEptide-Centric Analysis).cwl 
    in:
      PECAN (PEptide-Centric Analysis)_in_1: input_3
      PECAN (PEptide-Centric Analysis)_in_2: InDigestion_01/InDigestion_out_3
    out: [PECAN (PEptide-Centric Analysis)_out_1, PECAN (PEptide-Centric Analysis)_out_2]
  Mascot Server_05:
    run: add-path-to-the-implementation/Mascot Server.cwl 
    in:
      Mascot Server_in_1: PRIDE Toolsuite_03/PRIDE Toolsuite_out_1
      Mascot Server_in_2: PECAN (PEptide-Centric Analysis)_04/PECAN (PEptide-Centric Analysis)_out_2
    out: [Mascot Server_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3651" # MGF
    outputSource: Mascot Server_05/Mascot Server_out_1

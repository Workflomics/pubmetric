# WorkflowNo_333
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_333
doc: A workflow including the tool(s) ProteinProphet, PeptideProphet, OpenMS, MassChroQ, OpenSWATH.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3651" # MGF
  input_2:
    type: File
    format: "http://edamontology.org/format_2532" # GenBank-HTML
  input_3:
    type: File
    format: "http://edamontology.org/format_3311" # RNAML
steps:
  ProteinProphet_01:
    run: add-path-to-the-implementation/ProteinProphet.cwl 
    in:
      ProteinProphet_in_1: input_2
    out: [ProteinProphet_out_1]
  PeptideProphet_02:
    run: add-path-to-the-implementation/PeptideProphet.cwl 
    in:
      PeptideProphet_in_1: ProteinProphet_01/ProteinProphet_out_1
    out: [PeptideProphet_out_1]
  OpenMS_03:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_3
      OpenMS_in_2: input_1
      OpenMS_in_3: PeptideProphet_02/PeptideProphet_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  MassChroQ_04:
    run: add-path-to-the-implementation/MassChroQ.cwl 
    in:
      MassChroQ_in_1: OpenMS_03/OpenMS_out_1
    out: [MassChroQ_out_1]
  OpenSWATH_05:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: MassChroQ_04/MassChroQ_out_1
    out: [OpenSWATH_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
    outputSource: OpenSWATH_05/OpenSWATH_out_1

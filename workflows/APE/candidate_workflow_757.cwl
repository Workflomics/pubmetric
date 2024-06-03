# WorkflowNo_756
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_756
doc: A workflow including the tool(s) PeptideProphet, ProteinProphet, Comet, PeptideProphet, mzRecal, StPeter.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3655" # pepXML
  input_2:
    type: File
    format: "http://edamontology.org/format_3244" # mzML
  input_3:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
steps:
  PeptideProphet_01:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/PeptideProphet/PeptideProphet.cwl
    in:
      PeptideProphet_in_1: input_1
      PeptideProphet_in_2: input_2
      PeptideProphet_in_3: input_3
    out: [PeptideProphet_out_1, PeptideProphet_out_2]
  ProteinProphet_02:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/ProteinProphet/ProteinProphet.cwl
    in:
      ProteinProphet_in_1: PeptideProphet_01/PeptideProphet_out_1
      ProteinProphet_in_2: input_3
    out: [ProteinProphet_out_1, ProteinProphet_out_2]
  Comet_03:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/Comet/Comet.cwl
    in:
      Comet_in_1: input_2
      Comet_in_2: input_3
    out: [Comet_out_1, Comet_out_2]
  PeptideProphet_04:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/PeptideProphet/PeptideProphet.cwl
    in:
      PeptideProphet_in_1: input_1
      PeptideProphet_in_2: input_2
      PeptideProphet_in_3: input_3
    out: [PeptideProphet_out_1, PeptideProphet_out_2]
  mzRecal_05:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/mzRecal/mzRecal.cwl
    in:
      mzRecal_in_1: input_2
      mzRecal_in_2: Comet_03/Comet_out_2
    out: [mzRecal_out_1]
  StPeter_06:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/StPeter/StPeter.cwl
    in:
      StPeter_in_1: ProteinProphet_02/ProteinProphet_out_1
      StPeter_in_2: PeptideProphet_04/PeptideProphet_out_1
      StPeter_in_3: mzRecal_05/mzRecal_out_1
    out: [StPeter_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3747" # protXML
    outputSource: StPeter_06/StPeter_out_1

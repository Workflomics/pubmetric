# WorkflowNo_223
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_223
doc: A workflow including the tool(s) XTandem, mzRecal, PeptideProphet, ProteinProphet, protXml2IdList, gProfiler.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3244" # mzML
  input_2:
    type: File
    format: "http://edamontology.org/format_3247" # mzIdentML
  input_3:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
steps:
  XTandem_01:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/XTandem/XTandem.cwl
    in:
      XTandem_in_1: input_1
      XTandem_in_2: input_3
    out: [XTandem_out_1]
  mzRecal_02:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/mzRecal/mzRecal.cwl
    in:
      mzRecal_in_1: input_1
      mzRecal_in_2: input_2
    out: [mzRecal_out_1]
  PeptideProphet_03:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/PeptideProphet/PeptideProphet.cwl
    in:
      PeptideProphet_in_1: XTandem_01/XTandem_out_1
      PeptideProphet_in_2: mzRecal_02/mzRecal_out_1
      PeptideProphet_in_3: input_3
    out: [PeptideProphet_out_1, PeptideProphet_out_2]
  ProteinProphet_04:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/ProteinProphet/ProteinProphet.cwl
    in:
      ProteinProphet_in_1: PeptideProphet_03/PeptideProphet_out_1
      ProteinProphet_in_2: input_3
    out: [ProteinProphet_out_1, ProteinProphet_out_2]
  protXml2IdList_05:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/protXml2IdList/protXml2IdList.cwl
    in:
      protXml2IdList_in_1: ProteinProphet_04/ProteinProphet_out_1
    out: [protXml2IdList_out_1]
  gProfiler_06:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/gProfiler/gProfiler.cwl
    in:
      gProfiler_in_1: protXml2IdList_05/protXml2IdList_out_1
    out: [gProfiler_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3781" # PubAnnotation format
    outputSource: gProfiler_06/gProfiler_out_1

# Snakemake workflow for Chicago Food Inspections
# Run with: snakemake --cores 1

rule all:
    input:
        "clean_dataset.csv",
        "data_report.txt",
        "provenance.log"

rule process_data:
    input:
        inspections="food_inspections.csv",
        licenses="business_licenses.csv", 
        complaints="311_complaints.csv"
    output:
        dataset="clean_dataset.csv",
        report="data_report.txt",
        log="provenance.log"
    shell:
        "python workflow.py"

rule validate:
    input:
        "clean_dataset.csv"
    output:
        "validation_results.txt"
    shell:
        "python analysis.py > validation_results.txt"
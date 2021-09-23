{{/*
MIT License

(C) Copyright [2021] Hewlett Packard Enterprise Development LP

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
*/}}

{{/*
Application version to be applied to the job-name and to the images
registered.
*/}}
{{- define "update-uas.app-version" -}}
{{- default "latest" .Chart.AppVersion | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Labels commonly applied to jobs, adapted from cray-jobs
*/}}
{{- define "update-uas.labels" -}}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
{{ with .Values.job.labels -}}
{{ toYaml . -}}
{{- end -}}
{{- end -}}

{{/*
Annotations adapted from cray-service
*/}}
{{- define "update-uas.annotations" -}}
{{ with .Values.job.annotations -}}
{{ toYaml . -}}
{{- end -}}
{{- end -}}

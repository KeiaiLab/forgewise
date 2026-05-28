{{/*
ForgeWise Helm chart — template helpers
*/}}

{{/*
릴리즈 전체 이름 (release-name + chart-name 조합, 63자 제한).
*/}}
{{- define "forgewise.fullname" -}}
{{- if contains .Chart.Name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Chart 이름.
*/}}
{{- define "forgewise.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
공통 labels.
*/}}
{{- define "forgewise.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{ include "forgewise.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
selector labels (Deployment ↔ Service 매칭).
*/}}
{{- define "forgewise.selectorLabels" -}}
app.kubernetes.io/name: {{ include "forgewise.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
GitLab token Secret 이름.
existingSecret 이 지정되면 그것을, 아니면 chart 가 생성하는 Secret 이름.
*/}}
{{- define "forgewise.gitlabSecretName" -}}
{{- if .Values.gitlab.existingSecret }}
{{- .Values.gitlab.existingSecret }}
{{- else }}
{{- printf "%s-gitlab" (include "forgewise.fullname" .) }}
{{- end }}
{{- end }}

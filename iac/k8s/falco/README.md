# 🔒 Falco Security Demo on Kubernetes

This repository contains a demo setup for **[Falco](https://falco.org/)**, an open-source runtime security tool that detects unexpected behavior in containers and hosts. This guide includes installation, rule customization, Slack integration, and UI setup using **Helm** and **Falcosidekick**.

---

## 🚀 Prerequisites

- Kubernetes cluster (local or cloud)
- `kubectl` CLI configured
- [Helm](https://helm.sh/) installed
- Access to a Slack Webhook (optional for Slack alerting)

---

## 📦 Step-by-Step Setup

### 1. Add the Falco Helm Chart

```bash
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update
```

### 2. Install Falco with Helm

```bash
helm install --replace falco \
  --namespace falco \
  --create-namespace \
  --set tty=true \
  falcosecurity/falco
```

> This installs Falco in the `falco` namespace with basic settings.

---

### 3. Upgrade with Custom Rules and Enable Falcosidekick UI

```bash
helm upgrade -n falco falco falcosecurity/falco \
  -f custom_falco_rules.yaml \
  --set falcosidekick.enabled=true \
  --set falcosidekick.webui.enabled=true
```

> Ensure `custom_falco_rules.yaml` is in your working directory and includes your custom rules.

---

### 4. Access the Falcosidekick Web UI

```bash
kubectl port-forward -n falco svc/falco-falcosidekick-ui 2802
```

> Access the UI at: `http://localhost:2802`

---

### 5. (Optional) Enable Slack Integration for Alerts

```bash
helm upgrade -n falco falco falcosecurity/falco \
  --reuse-values \
  --set falcosidekick.config.slack.webhookurl="https://hooks.slack.com/services/TXXXX/BXXXX/XXXX" \
  --set falcosidekick.config.slack.outputformat="fields" \
  --set falcosidekick.config.slack.minimumpriority="warning"
```

> Replace the webhook URL with your own Slack Incoming Webhook.

---

## 🔍 Useful Commands

### Check Falco Resources

```bash
kubectl get po -n falco
kubectl get cm -n falco
```

### View Falco ConfigMap & Rules

```bash
kubectl get cm falco -n falco -o yaml
kubectl get cm falco-rules -n falco -o yaml
```

### View Falco Logs for Critical Alerts

```bash
kubectl logs <falco-pod-name> -n falco -f | grep "Critical Container"
```

> Replace `<falco-pod-name>` with your actual pod name. You can find it with `kubectl get po -n falco`.

---

## Demo Link
https://drive.google.com/file/d/1Svv0lSg4_Xgf6cVzdXJeduvUmRqtkQRy/view?usp=sharing

---

## 🛡️ About Falco

Falco lets you:

- Detect container breakouts
- Monitor system calls in real-time
- Create custom detection rules
- Trigger alerts to Slack, Webhooks, etc.

Learn more at: [https://falco.org/docs](https://falco.org/docs)

---

## 📄 License

This project follows the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0).

---

## 🙌 Acknowledgements

Thanks to the [Falco Security](https://github.com/falcosecurity) community and the maintainers of [Falcosidekick](https://github.com/falcosecurity/falcosidekick) for providing powerful tools to secure Kubernetes workloads.

---

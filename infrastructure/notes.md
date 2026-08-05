### `_iam_binding` — separate resource blocks, one per role

Each `_iam_binding` resource is scoped to exactly one role (the schema only takes a single role argument), so you can't combine multiple roles into one block. You need one resource per role:
```
resource "google_project_iam_binding" "owners" {
  project = "my-project"
  role    = "roles/owner"
  members = ["user:alice@example.com"]
}

resource "google_project_iam_binding" "viewers" {
  project = "my-project"
  role    = "roles/viewer"
  members = ["group:analytics@example.com"]
}
```

Each block is authoritative only for its own role. Other roles like `roles/editor` — untouched by either block — keeps whatever members it already had, whether they were set by console, gcloud, or another Terraform config. These two blocks can even live in different Terraform states/repos without conflicting, since they don't overlap in role.


### `_iam_policy` — one resource block for the whole resource, but multiple roles inside it

`_iam_policy` is authoritative for the entire policy on that resource, so you should only ever have one google_project_iam_policy resource per project. If you tried to have two, they'd fight each other on every apply (each would overwrite what the other set, since both think they own the whole policy).
To include multiple roles, you put multiple binding {} blocks inside a single `google_iam_policy` data source, then reference that in the one resource:
```
data "google_iam_policy" "project_policy" {
  binding {
    role    = "roles/owner"
    members = ["user:alice@example.com"]
  }
  binding {
    role    = "roles/viewer"
    members = ["group:analytics@example.com"]
  }
}

resource "google_project_iam_policy" "project" {
  project     = "my-project"
  policy_data = data.google_iam_policy.project_policy.policy_data
}
```
Here's the key danger: if `roles/editor` currently has bindings (from anywhere — console, another team, a previous gcloud grant) and you don't include a binding {} for `roles/editor` in the data source, applying this resource deletes those editor bindings entirely. `_iam_policy` doesn't merge with existing state — it replaces the whole policy wholesale with exactly what you declared, full stop.

### `_iam_member` is scoped to one role + one member per block
Like `_iam_binding` you need multiple resource blocks, but the granularity is even finer: you also need a separate block per member, not just per role. It applies additive grants, other existing role-member bindings never get touched
```
resource "google_project_iam_member" "owner_alice" {
  project = "my-project"
  role    = "roles/owner"
  member  = "user:alice@example.com"
}

resource "google_project_iam_member" "viewer_analytics" {
  project = "my-project"
  role    = "roles/viewer"
  member  = "group:analytics@example.com"
}

resource "google_project_iam_member" "viewer_bob" {
  project = "my-project"
  role    = "roles/viewer"
  member  = "user:bob@example.com"
}
```
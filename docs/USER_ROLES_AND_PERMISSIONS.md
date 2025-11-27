# User Roles and Permissions

## Overview

The Asset Movement Tracking System implements a role-based access control (RBAC) system with four distinct user roles. Each role has specific permissions that determine what actions users can perform within the system.

---

## Role Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    ASSET ADMINISTRATOR                          │
│                    (Full System Access)                         │
├─────────────────────────────────────────────────────────────────┤
│                    MOVEMENT APPROVER                            │
│                    (Approve & Manage Movements)                 │
├─────────────────────────────────────────────────────────────────┤
│                    ASSET OPERATOR                               │
│                    (Create Movement Requests)                   │
├─────────────────────────────────────────────────────────────────┤
│                    VIEWER                                       │
│                    (View Only Access)                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Role Definitions

### 1. Viewer (No Authority)
**Description:** Basic read-only access to the system. Suitable for stakeholders who need visibility but no operational control.

**Permissions:**
| Action | Allowed |
|--------|---------|
| View Dashboard | ✅ Yes |
| View Assets | ✅ Yes |
| View Asset Details | ✅ Yes |
| View Locations | ✅ Yes |
| View Movements | ✅ Yes |
| View Stock Takes | ✅ Yes |
| Create/Edit Assets | ❌ No |
| Create Movement Requests | ❌ No |
| Approve Movements | ❌ No |
| Manage Users | ❌ No |

---

### 2. Asset Operator (Group 1)
**Description:** Operational staff responsible for handling and moving assets. Can initiate movement requests that require approval.

**Permissions:**
| Action | Allowed |
|--------|---------|
| View Dashboard | ✅ Yes |
| View Assets | ✅ Yes |
| View Asset Details | ✅ Yes |
| View Locations | ✅ Yes |
| View Movements | ✅ Yes |
| View Stock Takes | ✅ Yes |
| Create Movement Requests | ✅ Yes (Pending Status) |
| Create/Edit Assets | ❌ No |
| Approve Movements | ❌ No |
| Complete/Deliver Movements | ❌ No |
| Manage Users | ❌ No |

**Notes:**
- Movement requests created by Asset Operators are automatically set to **Pending** status
- Requests must be approved by a Movement Approver or Asset Administrator

---

### 3. Movement Approver (Group 2)
**Description:** Supervisory role responsible for reviewing and approving movement requests. Can manage the movement workflow.

**Permissions:**
| Action | Allowed |
|--------|---------|
| View Dashboard | ✅ Yes |
| View Assets | ✅ Yes |
| View Asset Details | ✅ Yes |
| View Locations | ✅ Yes |
| View Movements | ✅ Yes |
| View Stock Takes | ✅ Yes |
| Create Movement Requests | ✅ Yes |
| Approve Pending Movements | ✅ Yes |
| Mark Movements as In Transit | ✅ Yes |
| Mark Movements as Completed | ✅ Yes |
| Mark Movements as Delivered | ✅ Yes |
| Create/Edit Assets | ❌ No |
| Manage Users | ❌ No |

**Restrictions:**
- ⚠️ **Cannot approve their own movement requests** - A different user must approve movements they initiated
- This ensures separation of duties and prevents unauthorized self-approval

---

### 4. Asset Administrator (Group 3)
**Description:** Full administrative access to the system. Responsible for asset management, system configuration, and user oversight.

**Permissions:**
| Action | Allowed |
|--------|---------|
| View Dashboard | ✅ Yes |
| View Assets | ✅ Yes |
| View Asset Details | ✅ Yes |
| View Locations | ✅ Yes |
| View Movements | ✅ Yes |
| View Stock Takes | ✅ Yes |
| **Create Assets** | ✅ Yes |
| **Edit Assets** | ✅ Yes |
| **Delete Assets** | ✅ Yes |
| Create Movement Requests | ✅ Yes |
| Approve Movements | ✅ Yes |
| Mark Movements as Completed/Delivered | ✅ Yes |
| Manage Categories | ✅ Yes |
| Manage Locations | ✅ Yes |
| View Activity Logs | ✅ Yes |
| View Reports | ✅ Yes |
| Access Django Admin | ✅ Yes |
| Manage Users | ✅ Yes |

**Notes:**
- Superusers bypass the self-approval restriction
- Has access to all administrative functions

---

## Permission Matrix

| Feature | Viewer | Asset Operator | Movement Approver | Asset Administrator |
|---------|--------|----------------|-------------------|---------------------|
| **Dashboard** |
| View Dashboard | ✅ | ✅ | ✅ | ✅ |
| View Reports | ❌ | ❌ | ❌ | ✅ |
| View Activity Log | ❌ | ❌ | ❌ | ✅ |
| **Assets** |
| View Asset List | ✅ | ✅ | ✅ | ✅ |
| View Asset Details | ✅ | ✅ | ✅ | ✅ |
| Create Asset | ❌ | ❌ | ❌ | ✅ |
| Edit Asset | ❌ | ❌ | ❌ | ✅ |
| Delete Asset | ❌ | ❌ | ❌ | ✅ |
| **Movements** |
| View Movements | ✅ | ✅ | ✅ | ✅ |
| Create Movement (Pending) | ❌ | ✅ | ✅ | ✅ |
| Approve Movement | ❌ | ❌ | ✅ | ✅ |
| Update Movement Status | ❌ | ❌ | ✅ | ✅ |
| **Locations** |
| View Locations | ✅ | ✅ | ✅ | ✅ |
| Manage Locations | ❌ | ❌ | ❌ | ✅ |
| **Stock Takes** |
| View Stock Takes | ✅ | ✅ | ✅ | ✅ |
| Create Stock Take | ❌ | ❌ | ✅ | ✅ |
| **Administration** |
| Manage Categories | ❌ | ❌ | ❌ | ✅ |
| Manage Users | ❌ | ❌ | ❌ | ✅ |
| Django Admin Access | ❌ | ❌ | ❌ | ✅ |

---

## Movement Workflow by Role

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Asset Operator  │     │Movement Approver │     │Asset Administrator│
│                  │     │                  │     │                  │
│  Creates Move    │────▶│  Reviews Move    │────▶│  Final Approval  │
│  (Pending)       │     │  Approves/Rejects│     │  (if needed)     │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Movement Status  │
                         │ - In Transit     │
                         │ - Completed      │
                         │ - Delivered      │
                         └──────────────────┘
```

### Movement Status Flow

1. **Pending** → Created by Asset Operator (awaiting approval)
2. **In Transit** → Approved and assets are being moved
3. **Completed** → Movement finished, assets at destination
4. **Delivered** → Final confirmation of delivery
5. **Cancelled** → Movement cancelled

---

## Security Rules

### Self-Approval Prevention
- Users **cannot approve their own movement requests**
- This rule applies to Movement Approvers
- Asset Administrators with superuser status may bypass this restriction
- Ensures proper separation of duties and audit compliance

### Activity Logging
All significant actions are logged in the Activity Log, including:
- User logins and logouts
- Asset creation, modification, and deletion
- Movement creation, approval, and status changes
- Stock take activities

---

## Setting Up User Roles

### Via Django Admin
1. Navigate to **Admin → Users**
2. Select the user to modify
3. In the **Role & Department** section, select the appropriate role
4. Save changes

### Bulk Role Assignment
1. In the User list, select multiple users
2. Use the **Actions** dropdown:
   - "Set selected users as Viewers (No Authority)"
   - "Set selected users as Asset Operators (Group 1)"
   - "Set selected users as Movement Approvers (Group 2)"
   - "Set selected users as Asset Administrators (Group 3)"
3. Click **Go**

### Via Management Command
```bash
python manage.py setup_user_groups
```
This command creates the permission groups with appropriate permissions.

---

## Best Practices

1. **Principle of Least Privilege**: Assign users the minimum role necessary for their job functions
2. **Separation of Duties**: Ensure movement creators and approvers are different people
3. **Regular Audits**: Review the Activity Log periodically for unusual activities
4. **Role Reviews**: Periodically review user roles and adjust as responsibilities change

---

## Contact

For access requests or role changes, please contact your system administrator.

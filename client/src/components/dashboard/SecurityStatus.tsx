import { Shield, Key, UserCheck } from "lucide-react";

export function SecurityStatus() {
  const securityItems = [
    {
      icon: Shield,
      label: "Encryption Status",
      status: "AES-256 Active",
      color: "text-green-600",
      testId: "security-encryption",
    },
    {
      icon: Key,
      label: "Key Management",
      status: "KMS Enabled",
      color: "text-blue-700",
      testId: "security-kms",
    },
    {
      icon: UserCheck,
      label: "Authentication",
      status: "Verified",
      color: "text-green-600",
      testId: "security-auth",
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mt-6">
      <h3 className="text-md font-semibold text-gray-900 mb-4">Security Status</h3>
      <div className="space-y-3">
        {securityItems.map((item) => (
          <div key={item.label} className="flex items-center justify-between" data-testid={item.testId}>
            <div className="flex items-center space-x-3">
              <item.icon className={item.color} size={20} />
              <span className="text-sm text-gray-700">{item.label}</span>
            </div>
            <span className={`text-sm font-medium ${item.color}`} data-testid={`status-${item.testId}`}>
              {item.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

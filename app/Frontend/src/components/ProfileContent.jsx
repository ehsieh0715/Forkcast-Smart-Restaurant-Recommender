import { useState, useEffect } from "react";
import Modal from "./Modal";
import { Edit } from "lucide-react";

export default function ProfileContent({ user }) {
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);
  const [formData, setFormData] = useState({
    username: user.username || "",
    name: user.name || "",
    email: user.email || "",
  });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (saveStatus) {
      const timer = setTimeout(() => setSaveStatus(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [saveStatus]);

  useEffect(() => {
    document.body.style.overflow = isEditing ? "hidden" : "auto";
    return () => {
      document.body.style.overflow = "auto";
    };
  }, [isEditing]);

  const validateForm = () => {
    const newErrors = {};
    if (!formData.username.trim()) {
      newErrors.username = "Username is required";
    } else if (formData.username.length < 3) {
      newErrors.username = "Username must be at least 3 characters";
    }

    if (!formData.name.trim()) {
      newErrors.name = "Full name is required";
    }

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Please enter a valid email";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const handleCancel = () => {
    setFormData({
      username: user.username || "",
      name: user.name || "",
      email: user.email || "",
    });
    setIsEditing(false);
    setErrors({});
    setSaveStatus(null);
  };

  const handleSave = async () => {
    if (!validateForm()) return;

    setIsSaving(true);
    setSaveStatus(null);

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/authentication/profile`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        },
      );

      if (!response.ok) {
        throw new Error("Failed to update profile");
      }

      setSaveStatus("success");
      setIsEditing(false);
      console.log("✅ Profile updated successfully:", formData);
    } catch (error) {
      console.error("❌ Error updating profile:", error);
      setSaveStatus("error");
    } finally {
      setIsSaving(false);
    }
  };

  const hasChanges = () => {
    return (
      formData.username !== user.username ||
      formData.name !== user.name ||
      formData.email !== user.email
    );
  };

  return (
    <div className="px-4 py-12">
      <div className="mx-auto max-w-2xl">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-24 w-24 items-center justify-center rounded-full bg-[#636AE8] shadow-lg">
            <span className="text-2xl font-bold text-white">
              {user.name ? user.name.charAt(0).toUpperCase() : "U"}
            </span>
          </div>
          <h1 className="mb-2 text-4xl font-bold text-gray-800">
            {user.name || "Your Profile"}
          </h1>
          <p className="text-gray-600">{user.email}</p>
        </div>

        {/* Status Messages */}
        {saveStatus === "success" && (
          <div className="mb-6 rounded-lg border border-green-200 bg-green-50 p-4 text-green-800">
            Profile updated successfully!
          </div>
        )}
        {saveStatus === "error" && (
          <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
            Failed to update profile. Please try again.
          </div>
        )}

        {/* Action Buttons */}
        <div className="mt-6 flex flex-col gap-3 sm:flex-row">
          <button
            className="m-auto w-1/2 cursor-pointer rounded-lg bg-[#636AE8] px-4 py-3 font-medium text-white hover:opacity-90"
            onClick={() => setIsEditing(true)}
          >
            <Edit className="mr-2 inline-block size-5" />
            <span>Edit Profile</span>
          </button>
        </div>

        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Last updated: {new Date().toLocaleDateString()}</p>
        </div>
      </div>

      {/* Edit Modal */}
      <Modal open={isEditing} onClose={handleCancel}>
        <h2 className="mb-4 text-xl font-bold text-gray-800">Edit Profile</h2>
        <div className="space-y-6">
          <Field
            label="Username"
            name="username"
            value={formData.username}
            editable
            onChange={handleChange}
            error={errors.username}
            placeholder="Enter your username"
          />
          <Field
            label="Full Name"
            name="name"
            value={formData.name}
            editable
            onChange={handleChange}
            error={errors.name}
            placeholder="Enter your full name"
          />
          <Field
            label="Email"
            name="email"
            value={formData.email}
            editable
            onChange={handleChange}
            error={errors.email}
            placeholder="Enter your email"
            type="email"
          />
          <div className="flex gap-3 pt-4">
            <button
              className="w-full cursor-pointer rounded-lg bg-[#636AE8] px-4 py-3 font-[600] text-white hover:opacity-90"
              onClick={handleSave}
              disabled={isSaving || !hasChanges()}
            >
              {isSaving ? "Saving..." : "Save Changes"}
            </button>
            <button
              className="w-full cursor-pointer rounded-lg bg-red-500 px-4 py-3 font-[600] text-white hover:opacity-90"
              onClick={handleCancel}
              disabled={isSaving}
            >
              Cancel
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

function Field({
  label,
  name,
  value,
  editable = false,
  onChange,
  error,
  placeholder,
  type = "text",
}) {
  return (
    <div>
      <label className="mb-2 block text-sm font-semibold text-gray-700">
        {label}
      </label>
      {editable ? (
        <div>
          <input
            type={type}
            name={name}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            className={`w-full rounded-lg border px-4 py-3 text-gray-800 transition-colors focus:ring-2 focus:outline-none ${
              error
                ? "border-red-300 bg-red-50 focus:ring-red-500"
                : "border-gray-300 focus:ring-blue-500"
            }`}
          />
          {error && (
            <p className="mt-1 flex items-center gap-1 text-sm text-red-600">
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
              {error}
            </p>
          )}
        </div>
      ) : (
        <div className="rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 text-gray-700">
          {value || "—"}
        </div>
      )}
    </div>
  );
}

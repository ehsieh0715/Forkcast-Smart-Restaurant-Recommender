import { X } from "lucide-react";

export default function Modal({ open, children, onClose }) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* 🔹 Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* 🔸 Modal Content */}
      <div className="relative z-10 max-h-7/8 w-[90%] max-w-[700px] overflow-x-hidden overflow-y-scroll rounded-2xl bg-white p-10 shadow-xl lg:max-w-[500px]">
        <X
          className="absolute top-10 right-5 size-6 cursor-pointer text-gray-500 hover:text-black"
          onClick={onClose}
        />
        {children}
      </div>
    </div>
  );
}

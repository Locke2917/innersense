"use client";
import { FaSearch, FaBell, FaCog, FaUserCircle } from "react-icons/fa";

export default function Topbar() {
  return (
    <div className="flex items-center justify-between bg-[#2E2E2E] p-3 text-white shadow-md">
      <div className="flex items-center space-x-3 w-2/3">
        <FaSearch className="text-lg" />
        <input type="text" placeholder="Search Innsersense" className="border p-2 rounded-lg w-full bg-gray-700 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none" />
      </div>
      <div className="flex items-center space-x-3">
        <FaBell className="text-gray-400 text-xl hover:text-white cursor-pointer" />
        <FaCog className="text-gray-400 text-xl hover:text-white cursor-pointer" />
        <FaUserCircle className="text-gray-400 text-xl hover:text-white cursor-pointer" />
      </div>
    </div>
  );
}
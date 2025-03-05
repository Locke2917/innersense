"use client";
import { FaHome, FaUsers, FaRegEnvelope, FaPhone, FaTasks, FaComments  } from "react-icons/fa";
import Link from "next/link";

export default function Sidebar() {
  return (
    <div className="w-14 bg-[#2E2E2E] text-white flex flex-col justify-between pb-4">
      <aside className="flex flex-col items-center p-3 space-y-4 mt-10">
        
      </aside>
      <aside className="flex flex-col items-center p-3 space-y-4">
        <Link href="/"><FaHome className="text-gray-400 text-xl hover:text-white cursor-pointer" /></Link>
        <Link href="/payers"><FaComments  className="text-gray-400 text-xl hover:text-white cursor-pointer mt-4" /></Link>
        <Link href="/users"><FaUsers className="text-gray-400 text-xl hover:text-white cursor-pointer mt-4" /></Link>
        <Link href="#"><FaRegEnvelope className="text-gray-400 text-xl hover:text-white cursor-pointer mt-2" /></Link>
        <Link href="#"><FaPhone className="text-gray-400 text-xl hover:text-white cursor-pointer mt-2" /></Link>
        <Link href="#"><FaTasks className="text-gray-400 text-xl hover:text-white cursor-pointer mt-2" /></Link>
      </aside>
    </div>
  );
}
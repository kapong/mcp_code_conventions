# MCP Code Convention

## Target

create mcp server that have 3 tools for help ai code agents, in general, to follow these rules/context/knowledge. include the following tools:

- **Project Overview**: อธิบายด้าน Business, ผู้ใช้เป้าหมาย, Feature หลักๆที่มี
- **Technology Stack**: ระบุ Tech Stack ที่ใช้จริงในโปรเจกต์
- **Project Structure**: กำหนดโครงสร้างโฟลเดอร์, ชื่อไฟล์, แนวทาง Architecture

แต่ละ Tool return เป็น Markdown string แบบง่ายๆ มี API สำหรับโยนไฟล์ที่ต้องใช้หรือแก้ไขไฟล์ที่มีอยู่สำหรับแต่ละ tools

แต่ละ Tool สามารถเรียกเก็บข้อมูลโดยแยกเป็น Project_id โดยมี default project_id เป็น "default" ที่โปรเจกอื่นสามารถ inherit ได้

## Technology Stack
- **Backend**: Python, FastAPI
- **Database**: PostgreSQL
- **System**: Docker, Docker Compose

## IMPORTANT
- docker compose should be start with docker host ssh, no local volume mount
- use python 3.12 or higher
- in requirement.txt don't use version pinning, use latest version
- use `uvicorn` as ASGI server
- use `uv` instead of pip
- update CLAUDE.md if there is any change in specification or implementation


using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

#pragma warning disable CA1814 // Prefer jagged arrays over multidimensional

namespace ECCD.Infrastructure.Persistence.Migrations
{
    /// <inheritdoc />
    public partial class SeedCdcs : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.InsertData(
                table: "ChildDevelopmentCenters",
                columns: new[] { "Id", "Address", "CreatedAt", "CreatedBy", "Name", "UpdatedAt", "UpdatedBy" },
                values: new object[,]
                {
                    { new Guid("11111111-1111-1111-1111-111111111111"), "Poblacion, Barangay Central", new DateTime(2026, 1, 1, 0, 0, 0, 0, DateTimeKind.Utc), null, "CDC Barangay Central", null, null },
                    { new Guid("22222222-2222-2222-2222-222222222222"), "Eastside, Barangay East", new DateTime(2026, 1, 1, 0, 0, 0, 0, DateTimeKind.Utc), null, "CDC Barangay East", null, null }
                });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DeleteData(
                table: "ChildDevelopmentCenters",
                keyColumn: "Id",
                keyValue: new Guid("11111111-1111-1111-1111-111111111111"));

            migrationBuilder.DeleteData(
                table: "ChildDevelopmentCenters",
                keyColumn: "Id",
                keyValue: new Guid("22222222-2222-2222-2222-222222222222"));
        }
    }
}

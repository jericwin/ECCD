using ECCD.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace ECCD.Infrastructure.Persistence.Configurations;

public class AttendanceConfiguration : IEntityTypeConfiguration<Attendance>
{
    public void Configure(EntityTypeBuilder<Attendance> builder)
    {
        builder.HasKey(a => a.Id);

        builder.HasIndex(a => new { a.LearnerId, a.ClassroomId, a.Date }).IsUnique();

        builder.Property(a => a.Remarks).HasMaxLength(500);

        builder.HasOne(a => a.Learner)
            .WithMany(l => l.AttendanceRecords)
            .HasForeignKey(a => a.LearnerId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasOne(a => a.Classroom)
            .WithMany(c => c.AttendanceRecords)
            .HasForeignKey(a => a.ClassroomId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}

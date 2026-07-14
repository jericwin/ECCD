using ECCD.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace ECCD.Infrastructure.Persistence.Configurations;

public class TeacherProfileConfiguration : IEntityTypeConfiguration<TeacherProfile>
{
    public void Configure(EntityTypeBuilder<TeacherProfile> builder)
    {
        builder.HasKey(t => t.Id);

        builder.Property(t => t.FullName).HasMaxLength(200).IsRequired();
        builder.Property(t => t.EmployeeId).HasMaxLength(50).IsRequired();
        builder.Property(t => t.Position).HasMaxLength(100).IsRequired();
        builder.Property(t => t.Mobile).HasMaxLength(20);
        builder.Property(t => t.Address).HasMaxLength(500);
        builder.Property(t => t.ProfilePhotoUrl).HasMaxLength(500);
        builder.Property(t => t.UserId).HasMaxLength(450).IsRequired();

        builder.HasIndex(t => t.EmployeeId).IsUnique();
        builder.HasIndex(t => t.UserId).IsUnique();

        builder.HasOne(t => t.Cdc)
            .WithMany()
            .HasForeignKey(t => t.CdcId)
            .OnDelete(DeleteBehavior.SetNull);
    }
}
